"""
Тесты аутентификации: регистрация, вход, выход, смена пароля.
"""

import pytest
from flask import url_for
from app.models import User


class TestAuth:
    """Тесты аутентификации."""

    def test_register_page(self, client):
        """Страница регистрации доступна."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Регистрация' in response.data

    def test_register_success(self, client, app):
        """Успешная регистрация нового пользователя."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'secret123',
            'password2': 'secret123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Регистрация прошла успешно' in response.data
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.name == 'New User'
            assert user.check_password('secret123')

    def test_register_username_taken(self, client, test_user):
        """Регистрация с занятым логином."""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'name': 'Another',
            'password': 'pass',
            'password2': 'pass'
        })
        assert response.status_code == 200
        assert b'Этот логин уже занят' in response.data

    def test_register_password_mismatch(self, client):
        """Пароли не совпадают."""
        response = client.post('/auth/register', data={
            'username': 'user2',
            'name': 'User',
            'password': 'pass1',
            'password2': 'pass2'
        })
        assert response.status_code == 200
        assert b'Пароли должны совпадать' in response.data

    def test_login_page(self, client):
        """Страница входа доступна."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Вход' in response.data

    def test_login_success(self, client, test_user):
        """Успешный вход."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Test User' in response.data  # имя пользователя в навбаре

    def test_login_wrong_password(self, client, test_user):
        """Неверный пароль."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrong'
        }, follow_redirects=True)
        assert b'Неверный логин или пароль' in response.data

    def test_login_nonexistent_user(self, client):
        """Несуществующий пользователь."""
        response = client.post('/auth/login', data={
            'username': 'nobody',
            'password': 'pass'
        }, follow_redirects=True)
        assert b'Неверный логин или пароль' in response.data

    def test_logout(self, auth_client):
        """Выход из системы."""
        response = auth_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Вы вышли из системы' in response.data

    def test_protected_route_redirect(self, client):
        """Неавторизованный пользователь перенаправляется на вход."""
        response = client.get('/create', follow_redirects=True)
        assert response.status_code == 200
        assert b'Вход' in response.data
        assert b'Пожалуйста, войдите' in response.data

    def test_change_password(self, auth_client, app, test_user):
        """Смена пароля."""
        response = auth_client.post('/profile/change_password', data={
            'old_password': 'password123',
            'new_password': 'newpass456',
            'new_password2': 'newpass456'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Пароль успешно изменен' in response.data
        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.check_password('newpass456')

    def test_change_password_wrong_old(self, auth_client):
        """Неверный текущий пароль при смене."""
        response = auth_client.post('/profile/change_password', data={
            'old_password': 'wrong',
            'new_password': 'newpass',
            'new_password2': 'newpass'
        })
        assert b'Неверный текущий пароль' in response.data