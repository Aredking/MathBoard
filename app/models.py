"""
Модели базы данных Math Board.
Содержит все ORM-модели: User, Task, Comment, Category, Like, Favorite, UserActionLog.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.constants import (
    USER_ROLE_USER,
    TASK_STATUS_ACTIVE,
    DIFFICULTY_MEDIUM,
    COMMENT_STATUS_ACTIVE,
)


class User(UserMixin, db.Model):
    """Модель пользователя"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256))

    # Профиль
    avatar = db.Column(db.String(255), nullable=True, default='default_avatar.png')
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)

    # Статус и роль
    role = db.Column(db.String(20), default=USER_ROLE_USER)
    email_confirmed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Статистика
    tasks_solved = db.Column(db.Integer, default=0)
    tasks_created = db.Column(db.Integer, default=0)
    total_likes_received = db.Column(db.Integer, default=0)
    reputation = db.Column(db.Integer, default=0)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    tasks = db.relationship('Task', backref='author', lazy='dynamic',
                           cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic',
                              cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic',
                           cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    action_logs = db.relationship('UserActionLog', backref='user', lazy='dynamic',
                                 cascade='all, delete-orphan')

    def set_password(self, password):
        """Устанавливает хеш пароля"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Проверяет пароль"""
        return check_password_hash(self.password_hash, password)

    def get_avatar_url(self):
        """Возвращает URL аватара"""
        if self.avatar and self.avatar != 'default_avatar.png':
            return f'/static/uploads/avatars/{self.avatar}'
        return '/static/uploads/avatars/default_avatar.png'

    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role == 'admin'

    def is_moderator(self):
        """Проверяет, является ли пользователь модератором"""
        return self.role in ['admin', 'moderator']

    def update_reputation(self):
        """Обновляет репутацию пользователя"""
        self.reputation = (
            self.tasks_solved * 10 +
            self.tasks_created * 5 +
            self.total_likes_received * 2
        )

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Сериализация для API"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar,
            'bio': self.bio,
            'role': self.role,
            'tasks_solved': self.tasks_solved,
            'tasks_created': self.tasks_created,
            'reputation': self.reputation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }


class Category(db.Model):
    """Модель категории задач"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#3498db')
    icon = db.Column(db.String(50), nullable=True)
    order = db.Column(db.Integer, default=0)

    tasks = db.relationship('Task', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color
        }


class Task(db.Model):
    """Модель задачи"""

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    solution = db.Column(db.Text, nullable=True)
    hint = db.Column(db.Text, nullable=True)

    # Метаданные
    difficulty = db.Column(db.String(20), default=DIFFICULTY_MEDIUM)
    status = db.Column(db.String(20), default=TASK_STATUS_ACTIVE)
    filename = db.Column(db.String(255), nullable=True)

    # Статистика
    views = db.Column(db.Integer, default=0)
    solves_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    # Отношения
    comments = db.relationship('Comment', backref='task', lazy='dynamic',
                              cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='task', lazy='dynamic',
                           cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='task', lazy='dynamic',
                               cascade='all, delete-orphan')

    def check_answer(self, user_answer):
        """Проверяет ответ пользователя"""
        if not user_answer:
            return False
        normalized_user = user_answer.strip().lower().replace(' ', '')
        normalized_correct = self.answer.strip().lower().replace(' ', '')
        return normalized_user == normalized_correct

    def increment_views(self):
        """Увеличивает счётчик просмотров"""
        self.views += 1
        db.session.commit()

    def is_liked_by(self, user):
        """Проверяет, лайкнул ли пользователь задачу"""
        if not user or not user.is_authenticated:
            return False
        return Like.query.filter_by(user_id=user.id, task_id=self.id).first() is not None

    def is_favorited_by(self, user):
        """Проверяет, добавил ли пользователь задачу в избранное"""
        if not user or not user.is_authenticated:
            return False
        return Favorite.query.filter_by(user_id=user.id, task_id=self.id).first() is not None

    def __repr__(self):
        return f'<Task {self.id}: {self.title[:30]}...>'

    def to_dict(self):
        """Сериализация для API"""
        return {
            'id': self.id,
            'title': self.title,
            'answer': self.answer,
            'solution': self.solution,
            'hint': self.hint,
            'difficulty': self.difficulty,
            'status': self.status,
            'views': self.views,
            'solves_count': self.solves_count,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'author': self.author.to_dict() if self.author else None,
            'category': self.category.to_dict() if self.category else None
        }


class Comment(db.Model):
    """Модель комментария"""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=COMMENT_STATUS_ACTIVE)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'author': self.author.to_dict() if self.author else None,
            'task_id': self.task_id,
            'parent_id': self.parent_id
        }


class Like(db.Model):
    """Модель лайка задачи"""

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='unique_user_task_like'),)


class Favorite(db.Model):
    """Модель избранного"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='unique_user_task_favorite'),)


class UserActionLog(db.Model):
    """Модель лога действий пользователя"""

    __tablename__ = 'user_action_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Statistics(db.Model):
    """Модель для хранения агрегированной статистики по дням"""

    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)

    total_users = db.Column(db.Integer, default=0)
    new_users = db.Column(db.Integer, default=0)
    total_tasks = db.Column(db.Integer, default=0)
    new_tasks = db.Column(db.Integer, default=0)
    total_solves = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)

    category_stats = db.Column(db.Text, nullable=True)  # JSON

    __table_args__ = (db.UniqueConstraint('date', name='unique_date'),)