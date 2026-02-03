"""
Константы бота: роли, паттерны callback'ов, метки.
"""

# Роли пользователей
ROLE_PLAYER = 'player'
ROLE_VOTER = 'voter'
ROLE_VIEWER = 'viewer'
ROLE_ADVISER = 'adviser'

ROLE_LABELS = {
    ROLE_PLAYER: 'Игрок',
    ROLE_VOTER: 'Судья',
    ROLE_VIEWER: 'Зритель',
    ROLE_ADVISER: 'Секундант',
}

AVAILABLE_ROLES = [
    (ROLE_PLAYER, ROLE_LABELS[ROLE_PLAYER]),
    (ROLE_VOTER, ROLE_LABELS[ROLE_VOTER]),
    (ROLE_VIEWER, ROLE_LABELS[ROLE_VIEWER]),
    (ROLE_ADVISER, ROLE_LABELS[ROLE_ADVISER]),
]

# Паттерны callback'ов для ConversationHandler
PATTERN_COMPETITION = r'^(comp_\d+|cancel)$'
PATTERN_ROLE = r'^(role_(player|voter|viewer|adviser)|cancel)$'
PATTERN_CONFIRM = r'^(confirm_yes|confirm_no)$'
PATTERN_EDIT_FIELD = r'^(edit_(name|phone|email|city|school|certificate|important)|cancel)$'
PATTERN_MORE_EDITS = r'^more_edits_(yes|no)$'
PATTERN_CERT_CHOICE = r'^cert_(yes|no)$'
PATTERN_MAIN_MENU = r'^(contact_usn|register_competition)$'
