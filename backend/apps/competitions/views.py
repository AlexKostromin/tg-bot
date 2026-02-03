from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from .models import Competition, VoterTimeSlot
from .serializers import CompetitionSerializer, VoterTimeSlotSerializer

class CompetitionViewSet(viewsets.ModelViewSet):
    """
    API endpoints для управления соревнованиями.
    
    Требует заголовок X-Admin-Token для доступа.
    
    list: Получить список всех соревнований
    create: Создать новое соревнование
    retrieve: Получить детали конкретного соревнования
    update: Обновить соревнование
    partial_update: Частичное обновление соревнования
    destroy: Удалить соревнование
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        token = self.request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Competition.objects.none()
        return Competition.objects.all().prefetch_related('arbitrators', 'voters', 'viewers', 'advisers')

    def list(self, request, *args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().create(request, *args, **kwargs)


class VoterTimeSlotViewSet(viewsets.ModelViewSet):
    """
    API endpoints для управления временными слотами судей в соревнованиях.
    
    Позволяет админам управлять расписанием судей.
    Требует заголовок X-Admin-Token для доступа.
    
    list: Получить список слотов (с фильтрацией по соревнованию и судье)
    create: Создать новый слот
    retrieve: Получить детали слота
    update: Обновить слот
    partial_update: Частичное обновление слота
    destroy: Удалить слот
    """
    queryset = VoterTimeSlot.objects.all()
    serializer_class = VoterTimeSlotSerializer
    filterset_fields = ['competition', 'voter', 'slot_date']
    ordering_fields = ['slot_date', 'start_time']
    ordering = ['slot_date', 'start_time']

    def get_queryset(self):
        token = self.request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return VoterTimeSlot.objects.none()
        return VoterTimeSlot.objects.select_related('competition', 'voter')

    def update(self, request, *args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if token != settings.ADMIN_TOKEN:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request, *args, **kwargs)
