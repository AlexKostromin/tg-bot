"""
Обёртки для работы с Django ORM через sync_to_async.
"""
from functools import wraps

from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.utils import timezone

from apps.users.models import User, ProfileChangeLog, NotificationOutbox, RegistrationRequest
from apps.competitions.models import Competition, VoterTimeSlot


def with_db_connection(func):
    """Закрывает устаревшие DB-соединения перед вызовом ORM."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        close_old_connections()
        try:
            return func(*args, **kwargs)
        finally:
            close_old_connections()
    return wrapper


@sync_to_async
@with_db_connection
def get_or_create_user(chat_id, telegram_id, username, first_name, last_name):
    """Get or create user from chat_id"""
    db_user, created = User.objects.get_or_create(
        chat_id=chat_id,
        defaults={
            'telegram_id': telegram_id,
            'username': username or '',
            'first_name': first_name or '',
            'last_name': last_name or '',
        }
    )
    if not created:
        db_user.telegram_id = telegram_id
        db_user.username = username or ''
        db_user.first_name = first_name or ''
        db_user.last_name = last_name or ''
        db_user.save()
    return db_user


@sync_to_async
@with_db_connection
def get_competitions():
    """Get all competitions"""
    return list(Competition.objects.all())


@sync_to_async
@with_db_connection
def get_competition_by_id(comp_id):
    """Get competition by ID"""
    return Competition.objects.get(id=comp_id)


@sync_to_async
@with_db_connection
def get_user_by_telegram_id(telegram_id):
    """Get user by telegram_id or raise DoesNotExist"""
    return User.objects.get(telegram_id=telegram_id)


@sync_to_async
@with_db_connection
def add_user_to_competition(user, comp, role):
    """Add user to competition's role list"""
    if role == 'player':
        comp.arbitrators.add(user)
    elif role == 'voter':
        comp.voters.add(user)
    elif role == 'viewer':
        comp.viewers.add(user)
    elif role == 'adviser':
        comp.advisers.add(user)


@sync_to_async
@with_db_connection
def update_or_create_new_user(
    chat_id,
    telegram_id,
    first_name,
    last_name,
    phone,
    email,
    country,
    city,
    school,
    company,
    position,
    certificate_name,
    important_info,
    birth_date=None,
    channel_name=None,
):
    """Update existing user created in start() with full profile data"""
    user = User.objects.get(chat_id=chat_id)
    user.telegram_id = telegram_id
    user.first_name = first_name
    user.last_name = last_name
    user.phone = phone
    user.email = email
    user.country = country
    user.city = city
    user.school = school
    user.company = company
    user.position = position
    user.certificate_name = certificate_name
    user.important_info = important_info
    if birth_date is not None:
        user.birth_date = birth_date
    if channel_name is not None:
        user.channel_name = channel_name
    user.save()
    return user


@sync_to_async
@with_db_connection
def create_profile_log(user: User, field_name, old_value, new_value) -> ProfileChangeLog:
    """Create profile change log"""
    return ProfileChangeLog.objects.create(
        user=user,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value
    )


@sync_to_async
@with_db_connection
def update_user_fields(user, **kwargs):
    """Update user fields and save"""
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()
    return user


@sync_to_async
@with_db_connection
def get_pending_outbox(limit: int) -> list:
    """
    Берём пачку задач на отправку.
    Важно: предполагается один экземпляр bot-процесса.
    """
    return list(
        NotificationOutbox.objects
        .filter(status=NotificationOutbox.STATUS_PENDING)
        .order_by('created_at')[:limit]
    )


@sync_to_async
@with_db_connection
def mark_outbox_sent(outbox_id: int):
    NotificationOutbox.objects.filter(id=outbox_id).update(
        status=NotificationOutbox.STATUS_SENT,
        sent_at=timezone.now(),
        last_error=None,
    )


@sync_to_async
@with_db_connection
def mark_outbox_failed(outbox_id: int, error: str, attempts: int, max_attempts: int):
    new_status = NotificationOutbox.STATUS_FAILED if attempts >= max_attempts else NotificationOutbox.STATUS_PENDING
    NotificationOutbox.objects.filter(id=outbox_id).update(
        status=new_status,
        attempts=attempts,
        last_error=error[:5000],
    )


@sync_to_async
@with_db_connection
def create_voter_time_slot(competition_id: int, voter_id: int, slot_date, start_time, end_time):
    """
    Создаёт временной слот для судьи в соревновании.
    """
    competition = Competition.objects.get(id=competition_id)
    voter = User.objects.get(id=voter_id)
    return VoterTimeSlot.objects.create(
        competition=competition,
        voter=voter,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
    )


@sync_to_async
@with_db_connection
def create_registration_request(user, competition, role):
    """
    Создаёт заявку на регистрацию (RegistrationRequest).
    Если заявка уже существует — возвращает существующую.
    """
    request, created = RegistrationRequest.objects.get_or_create(
        user=user,
        competition=competition,
        role=role,
        defaults={
            'user_first_name': user.first_name or '',
            'user_last_name': user.last_name or '',
            'user_email': user.email or '',
            'user_phone': user.phone or '',
        }
    )
    return request, created


@sync_to_async
@with_db_connection
def get_open_competitions_for_role(role):
    """
    Возвращает соревнования, для которых открыта регистрация по данной роли.
    """
    filter_field = f'entry_open_{role}'
    return list(Competition.objects.filter(**{filter_field: True}))


@sync_to_async
@with_db_connection
def get_open_roles_for_competition(competition):
    """
    Возвращает список ролей, для которых открыта регистрация в данном соревновании.
    """
    competition = Competition.objects.get(id=competition.id)
    roles = []
    if competition.entry_open_player:
        roles.append('player')
    if competition.entry_open_voter:
        roles.append('voter')
    if competition.entry_open_viewer:
        roles.append('viewer')
    if competition.entry_open_adviser:
        roles.append('adviser')
    return roles
