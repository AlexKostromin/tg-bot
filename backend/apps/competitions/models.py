from django.db import models
from apps.users.models import User

class Competition(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    entry_open_player = models.BooleanField(default=True, verbose_name='Открыта регистрация (Игроки)')
    entry_open_voter = models.BooleanField(default=True, verbose_name='Открыта регистрация (Судьи)')
    entry_open_viewer = models.BooleanField(default=True, verbose_name='Открыта регистрация (Зрители)')
    entry_open_adviser = models.BooleanField(default=True, verbose_name='Открыта регистрация (Секунданты)')
    
    arbitrators = models.ManyToManyField(User, related_name='competitions_as_arbitrator', blank=True, verbose_name='Игроки')
    voters = models.ManyToManyField(User, related_name='competitions_as_voter', blank=True, verbose_name='Судьи')
    viewers = models.ManyToManyField(User, related_name='competitions_as_viewer', blank=True, verbose_name='Зрители')
    advisers = models.ManyToManyField(User, related_name='competitions_as_adviser', blank=True, verbose_name='Секунданты')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        db_table = 'competitions_competition'
        verbose_name = 'Соревнование'
        verbose_name_plural = 'Соревнования'

    def __str__(self):
        return self.name


class VoterTimeSlot(models.Model):
    """
    Временные слоты для судей (Voters) в соревновании.
    Используется для указания времени, когда судья может судить.
    """
    
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='voter_time_slots',
        verbose_name='Соревнование',
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='voter_time_slots',
        verbose_name='Судья',
        limit_choices_to={'role': 'voter'},
    )
    
    slot_date = models.DateField(verbose_name='Дата слота')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    class Meta:
        db_table = 'competitions_votertimeslot'
        ordering = ['slot_date', 'start_time']
        unique_together = [('voter', 'competition', 'slot_date', 'start_time', 'end_time')]
        indexes = [
            models.Index(fields=['competition', 'slot_date']),
            models.Index(fields=['voter', 'competition']),
        ]
        verbose_name = 'Временной слот судьи'
        verbose_name_plural = 'Временные слоты судей'

    def __str__(self):
        return f"{self.voter.first_name} - {self.competition.name} ({self.slot_date} {self.start_time}-{self.end_time})"
