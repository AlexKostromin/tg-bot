from django.contrib import admin
from .models import User, ProfileChangeLog, NotificationOutbox, RegistrationRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Удобный список пользователей бота.
    """
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'email',
        'city',
        'created_at',
    )
    list_filter = ('role', 'is_active', 'country', 'city', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'chat_id', 'phone')
    readonly_fields = ('chat_id', 'telegram_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Основное', {
            'fields': ('chat_id', 'telegram_id', 'username', 'role', 'is_active'),
        }),
        ('Личные данные', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
                'birth_date',
                'channel_name',
            ),
        }),
        ('Профиль и рейтинги', {
            'fields': (
                'classic_rating',
                'quick_rating',
                'team_rating',
                'about',
                'certificate_name',
            ),
            'classes': ('collapse',),
        }),
        ('География и организация', {
            'fields': ('country', 'city', 'school', 'company', 'position'),
        }),
        ('Важная информация', {
            'fields': ('important_info',),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(ProfileChangeLog)
class ProfileChangeLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'field_name', 'changed_at')
    list_filter = ('field_name', 'changed_at')
    search_fields = ('user__username',)
    readonly_fields = ('user', 'field_name', 'old_value', 'new_value', 'changed_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(NotificationOutbox)
class NotificationOutboxAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'chat_id', 'user', 'attempts', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at', 'sent_at')
    search_fields = ('chat_id', 'user__username', 'user__first_name', 'user__last_name')


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    """
    Админ интерфейс для управления заявками на регистрацию участников.
    Позволяет одобрять и отклонять заявки.
    """
    list_display = ('id', 'user_display', 'role', 'competition', 'status', 'created_at')
    list_filter = ('status', 'role', 'competition', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'user_email', 'competition__name')
    readonly_fields = ('user', 'competition', 'created_at', 'reviewed_at', 'reviewed_by')
    
    fieldsets = (
        ('Заявка', {
            'fields': ('user', 'competition', 'role', 'status'),
        }),
        ('Снимок данных на момент заявки', {
            'fields': ('user_first_name', 'user_last_name', 'user_email', 'user_phone'),
        }),
        ('История рассмотрения', {
            'fields': ('created_at', 'reviewed_at', 'reviewed_by'),
        }),
    )
    
    def user_display(self, obj):
        return f"{obj.user_first_name} {obj.user_last_name} ({obj.user.username})"
    user_display.short_description = 'Участник'
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Одобрить заявки"""
        from django.utils import timezone
        updated = queryset.filter(status=RegistrationRequest.STATUS_PENDING).update(
            status=RegistrationRequest.STATUS_APPROVED,
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f"✓ Одобрено {updated} заявок")
    approve_requests.short_description = "✓ Одобрить заявки"
    
    def reject_requests(self, request, queryset):
        """Отклонить заявки"""
        from django.utils import timezone
        updated = queryset.filter(status=RegistrationRequest.STATUS_PENDING).update(
            status=RegistrationRequest.STATUS_REJECTED,
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f"✗ Отклонено {updated} заявок")
    reject_requests.short_description = "✗ Отклонить заявки"
