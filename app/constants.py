"""
Константы приложения Math Board.
"""

# Роли пользователей
USER_ROLE_USER = 'user'
USER_ROLE_MODERATOR = 'moderator'
USER_ROLE_ADMIN = 'admin'

USER_ROLES = [
    (USER_ROLE_USER, 'Пользователь'),
    (USER_ROLE_MODERATOR, 'Модератор'),
    (USER_ROLE_ADMIN, 'Администратор')
]

# Статусы задач
TASK_STATUS_ACTIVE = 'active'
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_ARCHIVED = 'archived'
TASK_STATUS_REJECTED = 'rejected'

TASK_STATUSES = [
    (TASK_STATUS_ACTIVE, 'Активна'),
    (TASK_STATUS_PENDING, 'На проверке'),
    (TASK_STATUS_ARCHIVED, 'В архиве'),
    (TASK_STATUS_REJECTED, 'Отклонена')
]

# Категории (для начального наполнения, slug генерируется автоматически)
DEFAULT_CATEGORIES = [
    ('Алгебра', 'algebra', '#3498db', 'bi-calculator'),
    ('Геометрия', 'geometry', '#2ecc71', 'bi-triangle'),
    ('Физика', 'physics', '#e74c3c', 'bi-lightning'),
    ('Математический анализ', 'calculus', '#9b59b6', 'bi-graph-up'),
    ('Статистика', 'statistics', '#f39c12', 'bi-bar-chart'),
    ('Тригонометрия', 'trigonometry', '#1abc9c', 'bi-circle'),
    ('Комбинаторика', 'combinatorics', '#e67e22', 'bi-diagram-3'),
]

# Сложность
DIFFICULTY_EASY = 'easy'
DIFFICULTY_MEDIUM = 'medium'
DIFFICULTY_HARD = 'hard'
DIFFICULTY_EXPERT = 'expert'

DIFFICULTIES = [
    (DIFFICULTY_EASY, 'Лёгкий'),
    (DIFFICULTY_MEDIUM, 'Средний'),
    (DIFFICULTY_HARD, 'Сложный'),
    (DIFFICULTY_EXPERT, 'Экспертный')
]

# Статусы комментариев
COMMENT_STATUS_ACTIVE = 'active'
COMMENT_STATUS_HIDDEN = 'hidden'
COMMENT_STATUS_DELETED = 'deleted'

COMMENT_STATUSES = [
    (COMMENT_STATUS_ACTIVE, 'Активен'),
    (COMMENT_STATUS_HIDDEN, 'Скрыт'),
    (COMMENT_STATUS_DELETED, 'Удалён')
]

# Типы действий
ACTION_TYPE_LOGIN = 'login'
ACTION_TYPE_LOGOUT = 'logout'
ACTION_TYPE_REGISTER = 'register'
ACTION_TYPE_CREATE_TASK = 'create_task'
ACTION_TYPE_EDIT_TASK = 'edit_task'
ACTION_TYPE_DELETE_TASK = 'delete_task'
ACTION_TYPE_SOLVE_TASK = 'solve_task'
ACTION_TYPE_ADD_COMMENT = 'add_comment'
ACTION_TYPE_LIKE_TASK = 'like_task'
ACTION_TYPE_FAVORITE_TASK = 'favorite_task'
ACTION_TYPE_UPDATE_PROFILE = 'update_profile'
ACTION_TYPE_UPLOAD_AVATAR = 'upload_avatar'

# Сообщения
SUCCESS_REGISTER = 'Регистрация прошла успешно! Теперь войдите.'
SUCCESS_LOGIN = 'Добро пожаловать, {}!'
SUCCESS_LOGOUT = 'Вы вышли из системы.'
SUCCESS_TASK_CREATED = 'Задача успешно создана!'
SUCCESS_TASK_UPDATED = 'Задача успешно обновлена!'
SUCCESS_TASK_DELETED = 'Задача удалена.'
SUCCESS_COMMENT_ADDED = 'Комментарий добавлен!'
SUCCESS_COMMENT_DELETED = 'Комментарий удалён.'
SUCCESS_PROFILE_UPDATED = 'Профиль успешно обновлён!'
SUCCESS_AVATAR_UPLOADED = 'Аватар успешно загружен!'
SUCCESS_ANSWER_CORRECT = '✅ Правильно! Отличная работа!'
SUCCESS_ANSWER_WRONG = '❌ Неверно. Попробуйте ещё раз!'

ERROR_USER_NOT_FOUND = 'Пользователь не найден'
ERROR_TASK_NOT_FOUND = 'Задача не найдена'
ERROR_PERMISSION_DENIED = 'У вас нет прав для выполнения этого действия'
ERROR_INVALID_CREDENTIALS = 'Неверный логин или пароль'