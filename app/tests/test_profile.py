"""
Тесты профиля пользователя.
"""

import pytest
from app.models import User
from app import db


class TestProfile:
    """Тесты профиля."""

    def test_view_profile(self, client, test_user):
        """Просмотр профиля пользователя."""
        response = client.get(f'/profile/{test_user.username}')
        assert response.status_code == 200
        assert f'{test_user.name}'.encode() in response.data

    def test_edit_profile(self, auth_client, app, test_user):
        """Редактирование профиля."""
        response = auth_client.post('/profile/edit', data={
            'name': 'New Name',
            'bio': 'New bio',
            'location': 'Moscow',
            'website': 'https://example.com'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'New Name' in response.data
        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.name == 'New Name'
            assert user.bio == 'New bio'

    def test_favorites_page(self, auth_client):
        """Страница избранного."""
        response = auth_client.get('/profile/favorites')
        assert response.status_code == 200
        assert b'Избранные задачи' in response.data

    def test_statistics_page(self, client):
        """Страница статистики."""
        response = client.get('/profile/statistics')
        assert response.status_code == 200
        assert b'Статистика' in response.data

    def test_about_page(self, client):
        """Страница 'О проекте'."""
        response = client.get('/profile/about')
        assert response.status_code == 200
        assert b'О проекте' in response.data