from django.db import models
from django.utils import timezone

ROLE_CHOICES = [
    ('player', 'Игрок'),
    ('voter', 'Судья'),
    ('viewer', 'Зритель'),
    ('adviser', 'Секундант'),
    ('admin', 'Администратор'),
]

class User(models.Model):
    chat_id = models.CharField(max_length=255, unique=True, verbose_name='ID чата')
    telegram_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='Telegram ID')
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Фамилия')
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name='Telegram username')
    email = models.EmailField(null=True, blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Телефон')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player', verbose_name='Роль')
    
    # Profile fields
    classic_rating = models.FloatField(null=True, blank=True, verbose_name='Рейтинг (классический)')
    quick_rating = models.FloatField(null=True, blank=True, verbose_name='Рейтинг (быстрый)')
    team_rating = models.FloatField(null=True, blank=True, verbose_name='Рейтинг (команда)')
    about = models.TextField(null=True, blank=True, verbose_name='О себе')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    channel_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Канал')
    certificate_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='ФИ для сертификата')
    country = models.CharField(max_length=255, null=True, blank=True, verbose_name='Страна')
    city = models.CharField(max_length=255, null=True, blank=True, verbose_name='Город')
    school = models.CharField(max_length=255, null=True, blank=True, verbose_name='Школа/Клуб')
    position = models.CharField(max_length=255, null=True, blank=True, verbose_name='Должность')
    company = models.CharField(max_length=255, null=True, blank=True, verbose_name='Компания')
    important_info = models.TextField(null=True, blank=True, verbose_name='Дополнительная информация')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        db_table = 'users_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.first_name} ({self.username})" if self.username else str(self.chat_id)


class ProfileChangeLog(models.Model):
    """Логирование изменений важной информации профиля"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='change_logs', verbose_name='Пользователь')
    field_name = models.CharField(max_length=255, verbose_name='Поле')
    old_value = models.TextField(null=True, blank=True, verbose_name='Старое значение')
    new_value = models.TextField(null=True, blank=True, verbose_name='Новое значение')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')

    class Meta:
        db_table = 'users_profilechangelog'
        ordering = ['-changed_at']
        verbose_name = 'Лог изменений'
        verbose_name_plural = 'Логи изменений'

    def __str__(self):
        return f"{self.user.username} - {self.field_name} - {self.changed_at}"


class NotificationOutbox(models.Model):
    """
    Outbox для рассылок: API складывает задачи, bot отправляет и помечает статусы.
    """

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notification_outbox',
        verbose_name='Пользователь',
    )
    chat_id = models.CharField(max_length=255, verbose_name='ID чата (Telegram)')
    message = models.TextField(verbose_name='Сообщение')

    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
        verbose_name='Статус',
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name='Попыток')
    last_error = models.TextField(null=True, blank=True, verbose_name='Последняя ошибка')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Отправлено')

    class Meta:
        db_table = 'users_notificationoutbox'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
        verbose_name = 'Outbox уведомлений'
        verbose_name_plural = 'Outbox уведомлений'

    def __str__(self):
        return f"Outbox#{self.id} {self.status} chat_id={self.chat_id}"


class RegistrationRequest(models.Model):
    """
    Заявка на регистрацию участника в соревновании.
    Используется для одобрения/отклонения заявок админом.
    """

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидание'),
        (STATUS_APPROVED, 'Одобрена'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registration_requests',
        verbose_name='Пользователь',
    )
    competition = models.ForeignKey(
        'competitions.Competition',
        on_delete=models.CASCADE,
        related_name='registration_requests',
        verbose_name='Соревнование',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Роль участника',
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
        verbose_name='Статус заявки',
    )
    
    # Сохраняем данные на момент регистрации (снимок)
    user_first_name = models.CharField(max_length=255, verbose_name='Имя (снимок)')
    user_last_name = models.CharField(max_length=255, verbose_name='Фамилия (снимок)')
    user_email = models.EmailField(verbose_name='Email (снимок)')
    user_phone = models.CharField(max_length=20, verbose_name='Телефон (снимок)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата рассмотрения')
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_registration_requests',
        verbose_name='Рассмотрено',
    )
    rejection_reason = models.TextField(null=True, blank=True, verbose_name='Причина отклонения')

    class Meta:
        db_table = 'users_registrationrequest'
        ordering = ['-created_at']
        unique_together = [('user', 'competition', 'role')]
        indexes = [
            models.Index(fields=['competition', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
        verbose_name = 'Заявка на регистрацию'
        verbose_name_plural = 'Заявки на регистрацию'

    def __str__(self):
        return f"{self.user.first_name} - {self.get_role_display()} - {self.competition.name} ({self.get_status_display()})"
