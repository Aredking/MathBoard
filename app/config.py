"""
Конфигурация приложения Math Board.
Содержит все настройки Flask и расширений.
"""

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    """Базовая конфигурация приложения"""

    # Безопасность
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-math-board-secret-key-2024'
    CSRF_ENABLED = True

    # База данных
    instance_path = os.path.join(basedir, '..', 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_path, 'mathboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Загрузка файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Пагинация
    TASKS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 15
    USERS_PER_PAGE = 20

    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = 86400  # 24 часа в секундах
    SESSION_COOKIE_SECURE = False  # True для HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Настройки кэширования
    SEND_FILE_MAX_AGE_DEFAULT = 3600  # 1 час


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        """Дополнительная настройка для продакшена"""
        import logging
        from logging.handlers import SysLogHandler

        # Отправка логов в syslog
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}