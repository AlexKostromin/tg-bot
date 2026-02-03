from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mass_mail
from django.conf import settings
from django.utils import timezone
from .models import User, NotificationOutbox, RegistrationRequest
from .serializers import UserSerializer, RegistrationRequestSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints для управления пользователями.
    
    Требует заголовок X-Admin-Token для доступа.
    
    list: Получить список всех пользователей
    retrieve: Получить детали конкретного пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Check admin token
        token = self.request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return User.objects.none()
        return User.objects.all()


class RegistrationRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoints для управления заявками на регистрацию.
    
    Позволяет админам одобрять и отклонять заявки участников.
    Требует заголовок X-Admin-Token для доступа.
    
    list: Получить список заявок (с фильтрацией по статусу и соревнованию)
    retrieve: Получить детали заявки
    update: Обновить заявку (изменить статус, причину отклонения)
    partial_update: Частичное обновление заявки
    approve: Одобрить заявку (action)
    reject: Отклонить заявку (action)
    """
    queryset = RegistrationRequest.objects.all()
    serializer_class = RegistrationRequestSerializer
    filterset_fields = ['status', 'competition', 'role']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        # Check admin token
        token = self.request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return RegistrationRequest.objects.none()
        return RegistrationRequest.objects.select_related('user', 'competition', 'reviewed_by')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Одобрить заявку на регистрацию"""
        token = request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        reg_request = self.get_object()
        if reg_request.status != RegistrationRequest.STATUS_PENDING:
            return Response(
                {
                    'error': (
                        'Только ожидающие заявки могут быть одобрены. '
                        f'Текущий статус: {reg_request.get_status_display()}'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        reg_request.status = RegistrationRequest.STATUS_APPROVED
        reg_request.reviewed_at = timezone.now()
        reg_request.reviewed_by = request.user if request.user.is_authenticated else None
        reg_request.save()
        
        # Добавляем пользователя в соревнование по его роли (идемпотентно)
        competition = reg_request.competition
        user = reg_request.user
        if reg_request.role == 'player':
            competition.arbitrators.add(user)
        elif reg_request.role == 'voter':
            competition.voters.add(user)
        elif reg_request.role == 'viewer':
            competition.viewers.add(user)
        elif reg_request.role == 'adviser':
            competition.advisers.add(user)
        
        return Response(
            RegistrationRequestSerializer(reg_request).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Отклонить заявку на регистрацию"""
        token = request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        reg_request = self.get_object()
        # В отличие от approve, здесь допускается отклонение как ожидающих,
        # так и ранее одобренных заявок (см. требования PDF).
        if reg_request.status not in (
            RegistrationRequest.STATUS_PENDING,
            RegistrationRequest.STATUS_APPROVED,
        ):
            return Response(
                {
                    'error': (
                        'Можно отклонять только ожидающие или одобренные заявки. '
                        f'Текущий статус: {reg_request.get_status_display()}'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        reason = request.data.get('reason', 'Причина не указана')
        competition = reg_request.competition
        user = reg_request.user
        previous_status = reg_request.status
        
        reg_request.status = RegistrationRequest.STATUS_REJECTED
        reg_request.reviewed_at = timezone.now()
        reg_request.reviewed_by = request.user if request.user.is_authenticated else None
        reg_request.rejection_reason = reason
        reg_request.save()

        # Если заявка была ранее одобрена — убираем пользователя из соревнования
        if previous_status == RegistrationRequest.STATUS_APPROVED and user is not None:
            if reg_request.role == 'player':
                competition.arbitrators.remove(user)
            elif reg_request.role == 'voter':
                competition.voters.remove(user)
            elif reg_request.role == 'viewer':
                competition.viewers.remove(user)
            elif reg_request.role == 'adviser':
                competition.advisers.remove(user)
        
        return Response(
            RegistrationRequestSerializer(reg_request).data,
            status=status.HTTP_200_OK
        )


class NotifyAPIView(APIView):
    """
    Отправка рассылок пользователям по различным каналам.
    
    POST /api/notify/
    
    Параметры:
    - message (обязательно): текст сообщения
    - subject (опционально): тема письма (для email)
    - role (опционально): фильтр по роли (player, voter, viewer, adviser, admin)
    - channels (опционально): список каналов ['tg', 'email']
    
    Требует заголовок X-Admin-Token.
    """
    def post(self, request):
        token = request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        message = request.data.get('message')
        role = request.data.get('role')
        channels = request.data.get('channels', [])
        subject = request.data.get('subject', 'Уведомление')

        if not message:
            return Response({'error': 'message required'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter users by role if specified
        if role:
            users = User.objects.filter(role=role)
        else:
            users = User.objects.all()

        results = []
        tg_enqueued = 0

        for user in users:
            result = {
                'id': user.id,
                'chat_id': user.chat_id,
                'email': user.email,
                'ok': True,
                'details': []
            }

            # Telegram: складываем в outbox (будет отправлено процессом bot)
            if not channels or 'tg' in channels:
                try:
                    NotificationOutbox.objects.create(
                        user=user,
                        chat_id=user.chat_id,
                        message=message,
                    )
                    tg_enqueued += 1
                    result['details'].append({'channel': 'tg', 'ok': True, 'queued': True})
                except Exception as e:
                    result['ok'] = False
                    result['details'].append({'channel': 'tg', 'ok': False, 'error': str(e)})

            # Send via Email
            if (not channels or 'email' in channels) and user.email:
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    result['details'].append({'channel': 'email', 'ok': True})
                except Exception as e:
                    result['ok'] = False
                    result['details'].append({'channel': 'email', 'ok': False, 'error': str(e)})

            results.append(result)

        return Response({
            'count': len(results),
            'tg_enqueued': tg_enqueued,
            'results': results
        })
