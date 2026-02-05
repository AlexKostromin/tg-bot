"""
Database service for async ORM operations with connection management.
Implements Single Responsibility Principle by organizing DB operations into logical groups.
"""
from datetime import date, time
from functools import wraps
from typing import Callable, List, Optional, Tuple, TypeVar

from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.utils import timezone

from apps.users.models import User, ProfileChangeLog, NotificationOutbox, RegistrationRequest
from apps.competitions.models import Competition, VoterTimeSlot

T = TypeVar('T')


def with_db_connection(func: Callable[..., T]) -> Callable[..., T]:
    """Closes old DB connections before ORM call and ensures cleanup."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        close_old_connections()
        try:
            return func(*args, **kwargs)
        finally:
            close_old_connections()
    return wrapper


class DatabaseService:
    """
    Centralized database service for all async ORM operations.
    Organizes operations by domain responsibility (Users, Competitions, Notifications, etc).
    """

    # ========== User Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_or_create_user(
        chat_id: str,
        telegram_id: str,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str]
    ) -> User:
        """Get or create user from chat_id."""
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

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_user_by_telegram_id(telegram_id: str) -> User:
        """Get user by telegram_id or raise DoesNotExist."""
        return User.objects.get(telegram_id=telegram_id)

    @staticmethod
    @sync_to_async
    @with_db_connection
    def update_or_create_new_user(
        chat_id: str,
        telegram_id: str,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        country: str,
        city: str,
        school: str,
        company: str,
        position: str,
        certificate_name: str,
        important_info: str,
        birth_date: Optional[date] = None,
        channel_name: Optional[str] = None,
    ) -> User:
        """Update or create user with full profile data."""
        user, created = User.objects.get_or_create(
            chat_id=chat_id,
            defaults={
                'telegram_id': telegram_id,
                'username': '',
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        # Always update with full profile data
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

    @staticmethod
    @sync_to_async
    @with_db_connection
    def update_user_fields(user: User, **kwargs) -> User:
        """Update user fields and save."""
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user

    # ========== Competition Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_competitions() -> List[Competition]:
        """Get all competitions."""
        return list(Competition.objects.all())

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_competition_by_id(comp_id: int) -> Competition:
        """Get competition by ID."""
        return Competition.objects.get(id=comp_id)

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_open_competitions_for_role(role: str) -> List[Competition]:
        """Get competitions with registration open for the given role."""
        filter_field = f'entry_open_{role}'
        return list(Competition.objects.filter(**{filter_field: True}))

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_open_roles_for_competition(competition: Competition) -> List[str]:
        """Get list of roles with open registration for this competition."""
        competition = Competition.objects.get(id=competition.id)
        roles: List[str] = []
        if competition.entry_open_player:
            roles.append('player')
        if competition.entry_open_voter:
            roles.append('voter')
        if competition.entry_open_viewer:
            roles.append('viewer')
        if competition.entry_open_adviser:
            roles.append('adviser')
        return roles

    # ========== Competition-User Relationship Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def add_user_to_competition(user: User, comp: Competition, role: str) -> None:
        """Add user to competition's role list."""
        if role == 'player':
            comp.arbitrators.add(user)
        elif role == 'voter':
            comp.voters.add(user)
        elif role == 'viewer':
            comp.viewers.add(user)
        elif role == 'adviser':
            comp.advisers.add(user)

    # ========== Profile Audit Log Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def create_profile_log(user: User, field_name: str, old_value: str, new_value: str) -> ProfileChangeLog:
        """Create profile change log entry."""
        return ProfileChangeLog.objects.create(
            user=user,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )

    # ========== Registration Request Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def create_registration_request(user: User, competition: Competition, role: str) -> Tuple[RegistrationRequest, bool]:
        """Create registration request (returns existing if already created)."""
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

    # ========== Voter Time Slot Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def create_voter_time_slot(
        competition_id: int,
        voter_id: int,
        slot_date: date,
        start_time: time,
        end_time: time
    ) -> VoterTimeSlot:
        """Create time slot for voter in competition."""
        competition = Competition.objects.get(id=competition_id)
        voter = User.objects.get(id=voter_id)
        return VoterTimeSlot.objects.create(
            competition=competition,
            voter=voter,
            slot_date=slot_date,
            start_time=start_time,
            end_time=end_time,
        )

    # ========== Notification Outbox Operations ==========

    @staticmethod
    @sync_to_async
    @with_db_connection
    def get_pending_outbox(limit: int) -> List[NotificationOutbox]:
        """Get batch of pending notifications (assumes single bot instance)."""
        return list(
            NotificationOutbox.objects
            .filter(status=NotificationOutbox.STATUS_PENDING)
            .order_by('created_at')[:limit]
        )

    @staticmethod
    @sync_to_async
    @with_db_connection
    def mark_outbox_sent(outbox_id: int) -> None:
        """Mark notification as sent."""
        NotificationOutbox.objects.filter(id=outbox_id).update(
            status=NotificationOutbox.STATUS_SENT,
            sent_at=timezone.now(),
            last_error=None,
        )

    @staticmethod
    @sync_to_async
    @with_db_connection
    def mark_outbox_failed(outbox_id: int, error: str, attempts: int, max_attempts: int) -> None:
        """Mark notification as failed, or retry if under max attempts."""
        new_status = NotificationOutbox.STATUS_FAILED if attempts >= max_attempts else NotificationOutbox.STATUS_PENDING
        NotificationOutbox.objects.filter(id=outbox_id).update(
            status=new_status,
            attempts=attempts,
            last_error=error[:5000],
        )


# ========== Backward Compatibility Wrappers ==========
# These maintain the old API for existing code that hasn't been refactored yet.

@sync_to_async
@with_db_connection
def get_or_create_user(chat_id: str, telegram_id: str, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> User:
    """Deprecated: Use DatabaseService.get_or_create_user instead."""
    return User.objects.get_or_create(
        chat_id=chat_id,
        defaults={
            'telegram_id': telegram_id,
            'username': username or '',
            'first_name': first_name or '',
            'last_name': last_name or '',
        }
    )[0]


@sync_to_async
@with_db_connection
def get_competitions() -> List[Competition]:
    """Deprecated: Use DatabaseService.get_competitions instead."""
    return list(Competition.objects.all())


@sync_to_async
@with_db_connection
def get_competition_by_id(comp_id: int) -> Competition:
    """Deprecated: Use DatabaseService.get_competition_by_id instead."""
    return Competition.objects.get(id=comp_id)


@sync_to_async
@with_db_connection
def get_user_by_telegram_id(telegram_id: str) -> User:
    """Deprecated: Use DatabaseService.get_user_by_telegram_id instead."""
    return User.objects.get(telegram_id=telegram_id)


@sync_to_async
@with_db_connection
def add_user_to_competition(user: User, comp: Competition, role: str) -> None:
    """Deprecated: Use DatabaseService.add_user_to_competition instead."""
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
    chat_id: str,
    telegram_id: str,
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    country: str,
    city: str,
    school: str,
    company: str,
    position: str,
    certificate_name: str,
    important_info: str,
    birth_date: Optional[date] = None,
    channel_name: Optional[str] = None,
) -> User:
    """Deprecated: Use DatabaseService.update_or_create_new_user instead."""
    user, created = User.objects.get_or_create(
        chat_id=chat_id,
        defaults={
            'telegram_id': telegram_id,
            'username': '',
            'first_name': first_name,
            'last_name': last_name,
        }
    )
    # Always update with full profile data
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
def create_profile_log(user: User, field_name: str, old_value: str, new_value: str) -> ProfileChangeLog:
    """Deprecated: Use DatabaseService.create_profile_log instead."""
    return ProfileChangeLog.objects.create(
        user=user,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value
    )


@sync_to_async
@with_db_connection
def update_user_fields(user: User, **kwargs) -> User:
    """Deprecated: Use DatabaseService.update_user_fields instead."""
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()
    return user


@sync_to_async
@with_db_connection
def get_pending_outbox(limit: int) -> List[NotificationOutbox]:
    """Deprecated: Use DatabaseService.get_pending_outbox instead."""
    return list(
        NotificationOutbox.objects
        .filter(status=NotificationOutbox.STATUS_PENDING)
        .order_by('created_at')[:limit]
    )


@sync_to_async
@with_db_connection
def mark_outbox_sent(outbox_id: int) -> None:
    """Deprecated: Use DatabaseService.mark_outbox_sent instead."""
    NotificationOutbox.objects.filter(id=outbox_id).update(
        status=NotificationOutbox.STATUS_SENT,
        sent_at=timezone.now(),
        last_error=None,
    )


@sync_to_async
@with_db_connection
def mark_outbox_failed(outbox_id: int, error: str, attempts: int, max_attempts: int) -> None:
    """Deprecated: Use DatabaseService.mark_outbox_failed instead."""
    new_status = NotificationOutbox.STATUS_FAILED if attempts >= max_attempts else NotificationOutbox.STATUS_PENDING
    NotificationOutbox.objects.filter(id=outbox_id).update(
        status=new_status,
        attempts=attempts,
        last_error=error[:5000],
    )


@sync_to_async
@with_db_connection
def create_voter_time_slot(
    competition_id: int,
    voter_id: int,
    slot_date: date,
    start_time: time,
    end_time: time
) -> VoterTimeSlot:
    """Deprecated: Use DatabaseService.create_voter_time_slot instead."""
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
def create_registration_request(user: User, competition: Competition, role: str) -> Tuple[RegistrationRequest, bool]:
    """Deprecated: Use DatabaseService.create_registration_request instead."""
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
def get_open_competitions_for_role(role: str) -> List[Competition]:
    """Deprecated: Use DatabaseService.get_open_competitions_for_role instead."""
    filter_field = f'entry_open_{role}'
    return list(Competition.objects.filter(**{filter_field: True}))


@sync_to_async
@with_db_connection
def get_open_roles_for_competition(competition: Competition) -> List[str]:
    """Deprecated: Use DatabaseService.get_open_roles_for_competition instead."""
    competition = Competition.objects.get(id=competition.id)
    roles: List[str] = []
    if competition.entry_open_player:
        roles.append('player')
    if competition.entry_open_voter:
        roles.append('voter')
    if competition.entry_open_viewer:
        roles.append('viewer')
    if competition.entry_open_adviser:
        roles.append('adviser')
    return roles
