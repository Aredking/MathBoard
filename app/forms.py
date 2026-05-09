"""
Формы Flask-WTF для Math Board.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    TextAreaField, SelectField, IntegerField, HiddenField, EmailField
)
from wtforms.validators import (
    DataRequired, Length, EqualTo, ValidationError, Optional,
    Email, URL, NumberRange, Regexp
)
from flask_login import current_user
from app.models import User, Category
from app.constants import DIFFICULTIES, TASK_STATUSES


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(), Length(min=3, max=64),
        Regexp(r'^[A-Za-z0-9_]+$', message='Только буквы, цифры и подчёркивание')
    ])
    name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Этот логин уже занят.')

    def validate_email(self, email):
        if email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Этот email уже используется.')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ProfileEditForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[Optional(), Email(), Length(max=120)])
    bio = TextAreaField('О себе', validators=[Optional(), Length(max=500)])
    location = StringField('Местоположение', validators=[Optional(), Length(max=100)])
    website = StringField('Веб-сайт', validators=[Optional(), URL()])
    avatar = FileField('Аватар', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')])
    submit = SubmitField('Сохранить')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('Повторите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Сменить пароль')

    def validate_old_password(self, old_password):
        if not current_user.check_password(old_password.data):
            raise ValidationError('Неверный текущий пароль')


class TaskForm(FlaskForm):
    title = TextAreaField('Условие задачи', validators=[DataRequired(), Length(max=1000)])
    answer = StringField('Правильный ответ', validators=[DataRequired(), Length(max=255)])
    solution = TextAreaField('Решение (необязательно)', validators=[Optional()])
    hint = TextAreaField('Подсказка', validators=[Optional(), Length(max=500)])
    category = SelectField('Категория', coerce=int, validators=[Optional()])
    difficulty = SelectField('Сложность', choices=[(d[0], d[1]) for d in DIFFICULTIES])
    file = FileField('Прикрепить файл', validators=[Optional(), FileAllowed(['txt', 'pdf', 'jpg', 'png'], 'Разрешены txt, pdf, изображения')])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by('order').all()]


class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=2, max=1000)])
    task_id = HiddenField(validators=[DataRequired()])
    parent_id = HiddenField()
    submit = SubmitField('Отправить')


class SearchForm(FlaskForm):
    q = StringField('Поиск', validators=[Optional()])
    category = SelectField('Категория', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    difficulty = SelectField('Сложность', choices=[('', 'Все')] + [(d[0], d[1]) for d in DIFFICULTIES])
    status = SelectField('Статус', choices=[('', 'Все')] + [(s[0], s[1]) for s in TASK_STATUSES])
    sort_by = SelectField('Сортировка', choices=[
        ('created_at_desc', 'Новые'),
        ('created_at_asc', 'Старые'),
        ('likes_desc', 'По лайкам'),
        ('solves_desc', 'По решениям'),
        ('views_desc', 'По просмотрам')
    ])
    submit = SubmitField('Применить')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [('', 'Все категории')] + [(c.id, c.name) for c in Category.query.all()]


class AdminUserEditForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=64)])
    name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[Optional(), Email()])
    role = SelectField('Роль', choices=[('user','Пользователь'),('moderator','Модератор'),('admin','Админ')])
    is_active = BooleanField('Активен')
    reputation = IntegerField('Репутация', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Сохранить')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Логин уже используется')


class AdminTaskModerateForm(FlaskForm):
    status = SelectField('Статус', choices=[(s[0], s[1]) for s in TASK_STATUSES])
    reason = TextAreaField('Причина изменения', validators=[Optional()])
    submit = SubmitField('Применить')


class AnswerCheckForm(FlaskForm):
    answer = StringField('Ответ', validators=[DataRequired()])
    task_id = HiddenField(validators=[DataRequired()])