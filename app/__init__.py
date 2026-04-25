"""
Фабрика приложения Flask для Math Board.
Инициализирует все расширения и регистрирует blueprints.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect
from logging.handlers import RotatingFileHandler

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
rest_api = Api(prefix='/api/v2')


def create_app(config_class=None):
    """
    Создаёт и настраивает экземпляр приложения Flask.

    Args:
        config_class: Класс конфигурации. По умолчанию Config из app.config

    Returns:
        Flask: Настроенный экземпляр приложения
    """
    if config_class is None:
        config_class = os.environ.get('FLASK_CONFIG', 'app.config.Config')

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    rest_api.init_app(app)

    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'

    # Регистрация blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp)

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.comments import bp as comments_bp
    app.register_blueprint(comments_bp, url_prefix='/comments')

    # Регистрация обработчиков ошибок
    from app.errors import handlers
    handlers.register_error_handlers(app)

    # Регистрация API ресурсов
    from app.api.resources import (
        TaskListResource, TaskResource,
        UserListResource, UserResource,
        CommentListResource, CommentResource,
        CategoryListResource, StatisticsResource
    )
    rest_api.add_resource(TaskListResource, '/tasks')
    rest_api.add_resource(TaskResource, '/tasks/<int:task_id>')
    rest_api.add_resource(UserListResource, '/users')
    rest_api.add_resource(UserResource, '/users/<int:user_id>')
    rest_api.add_resource(CommentListResource, '/comments')
    rest_api.add_resource(CommentResource, '/comments/<int:comment_id>')
    rest_api.add_resource(CategoryListResource, '/categories')
    rest_api.add_resource(StatisticsResource, '/statistics')

    # Создание папок для загрузок
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'tasks')
    app.config['AVATAR_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

    # Настройка логирования
    setup_logging(app)

    # Импорт моделей для создания таблиц
    from app.models import User, Task, Comment, Category, Like, Favorite, UserActionLog, Statistics

    @login_manager.user_loader
    def load_user(user_id):
        """Загрузка пользователя по ID для Flask-Login"""
        return User.query.get(int(user_id))

    # Добавление глобальных переменных в шаблоны
    @app.context_processor
    def inject_categories():
        """Добавляет категории во все шаблоны"""
        return {'categories': Category.query.all()}

    return app


def setup_logging(app):
    """Настройка логирования для приложения"""
    if not app.debug:
        # Создаём папку для логов
        log_dir = os.path.join(os.path.dirname(app.root_path), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # Настройка файлового обработчика
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'mathboard.log'),
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Math Board запущен')