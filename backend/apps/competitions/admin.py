from django.contrib import admin
from .models import Competition, VoterTimeSlot
from apps.users.models import User


class VoterTimeSlotsInline(admin.TabularInline):
    """Встроенное редактирование временных слотов судей"""
    model = VoterTimeSlot
    extra = 1
    fields = ('voter', 'slot_date', 'start_time', 'end_time')
    ordering = ('slot_date', 'start_time')

    def get_formset(self, request, obj=None, **kwargs):
        """Ограничиваем список судей в выпадающем списке только теми, кто добавлен в соревнование.

        Если объект `obj` (соревнование) доступен, используем его `voters` M2M.
        При создании нового соревнования (obj is None) показываем всех пользователей с ролью 'voter'.
        """
        formset = super().get_formset(request, obj, **kwargs)
        try:
            if hasattr(formset.form, 'base_fields') and 'voter' in formset.form.base_fields:
                if obj is not None:
                    formset.form.base_fields['voter'].queryset = obj.voters.all()
                else:
                    formset.form.base_fields['voter'].queryset = User.objects.filter(role='voter')
        except Exception:
            pass
        return formset


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """
    Красивый список соревнований с быстрым доступом к статусам и ролям.
    """
    list_display = (
        'name',
        'count_arbitrators',
        'count_voters',
        'count_viewers',
        'count_advisers',
        'entry_open_player',
        'entry_open_voter',
        'created_at',
    )
    list_filter = (
        'entry_open_player',
        'entry_open_voter',
        'entry_open_viewer',
        'entry_open_adviser',
        'created_at',
    )
    search_fields = ('name', 'description')
    filter_horizontal = ('arbitrators', 'voters', 'viewers', 'advisers')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    inlines = [VoterTimeSlotsInline]

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'description', 'created_at'),
        }),
        ('Открыта регистрация для ролей', {
            'fields': (
                'entry_open_player',
                'entry_open_voter',
                'entry_open_viewer',
                'entry_open_adviser',
            ),
            'description': 'Какие роли могут регистрироваться через бота на это соревнование.',
        }),
        ('Участники по ролям (выберите из списка слева)', {
            'fields': ('arbitrators', 'voters', 'viewers', 'advisers'),
            'classes': ('wide',),  # Добавляем wide класс для лучшего отображения
            'description': 'Используйте стрелки (→/←) для добавления/удаления участников',
        }),
    )
    
    def count_arbitrators(self, obj):
        return obj.arbitrators.count()
    count_arbitrators.short_description = 'Игроков'
    
    def count_voters(self, obj):
        return obj.voters.count()
    count_voters.short_description = 'Судей'
    
    def count_viewers(self, obj):
        return obj.viewers.count()
    count_viewers.short_description = 'Зрителей'
    
    def count_advisers(self, obj):
        return obj.advisers.count()
    count_advisers.short_description = 'Секундантов'


@admin.register(VoterTimeSlot)
class VoterTimeSlotAdmin(admin.ModelAdmin):
    """
    Админ интерфейс для управления временными слотами судей.
    """
    list_display = ('id', 'voter_name', 'competition', 'slot_date', 'start_time', 'end_time')
    list_filter = ('competition', 'slot_date')
    search_fields = ('voter__first_name', 'voter__last_name', 'competition__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Основное', {
            'fields': ('competition', 'voter')
        }),
        ('Время', {
            'fields': ('slot_date', 'start_time', 'end_time')
        }),
        ('История', {
            'fields': ('created_at',)
        }),
    )
    
    def voter_name(self, obj):
        return f"{obj.voter.first_name} {obj.voter.last_name}"
    voter_name.short_description = 'Судья'
