"""
Тесты REST API.
"""

import json
import pytest
from app.models import Task, User


class TestTaskAPI:
    """Тесты API задач."""

    def test_get_tasks_list(self, client, test_task):
        """GET /api/v2/tasks возвращает список задач."""
        response = client.get('/api/v2/tasks')
        assert response.status_code == 200
        data = response.get_json()
        assert 'tasks' in data
        assert len(data['tasks']) >= 1

    def test_get_single_task(self, client, test_task):
        """GET /api/v2/tasks/<id> возвращает задачу."""
        response = client.get(f'/api/v2/tasks/{test_task.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Тестовая задача'

    def test_get_task_not_found(self, client):
        """GET несуществующей задачи возвращает 404."""
        response = client.get('/api/v2/tasks/99999')
        assert response.status_code == 404

    def test_create_task_api(self, auth_client, app):
        """POST /api/v2/tasks создаёт задачу."""
        with app.app_context():
            from app.models import Category
            cat_id = Category.query.first().id
        response = auth_client.post('/api/v2/tasks', json={
            'title': 'API задача',
            'answer': '123',
            'difficulty': 'medium',
            'category_id': cat_id
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'API задача'

    def test_create_task_unauthorized(self, client):
        """POST без авторизации возвращает 401."""
        response = client.post('/api/v2/tasks', json={'title': 'test'})
        assert response.status_code == 401

    def test_update_task_api(self, auth_client, test_task):
        """PUT /api/v2/tasks/<id> обновляет задачу."""
        response = auth_client.put(f'/api/v2/tasks/{test_task.id}', json={
            'title': 'Обновлено через API',
            'answer': 'новый ответ'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Обновлено через API'

    def test_delete_task_api(self, auth_client, test_task, app):
        """DELETE /api/v2/tasks/<id> удаляет задачу."""
        response = auth_client.delete(f'/api/v2/tasks/{test_task.id}')
        assert response.status_code == 200
        with app.app_context():
            assert Task.query.get(test_task.id) is None


class TestUserAPI:
    """Тесты API пользователей."""

    def test_get_users_list(self, client):
        """GET /api/v2/users возвращает список пользователей."""
        response = client.get('/api/v2/users')
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data

    def test_get_single_user(self, client, test_user):
        """GET /api/v2/users/<id> возвращает пользователя."""
        response = client.get(f'/api/v2/users/{test_user.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'testuser'

    def test_create_user_api_admin(self, admin_client, app):
        """POST /api/v2/users (только админ)."""
        response = admin_client.post('/api/v2/users', json={
            'username': 'apiuser',
            'name': 'API User',
            'password': 'pass123'
        })
        assert response.status_code == 201
        with app.app_context():
            user = User.query.filter_by(username='apiuser').first()
            assert user is not None

    def test_create_user_api_forbidden(self, auth_client):
        """Обычный пользователь не может создать пользователя через API."""
        response = auth_client.post('/api/v2/users', json={'username': 'hack'})
        assert response.status_code == 403


class TestCommentAPI:
    """Тесты API комментариев."""

    def test_get_comments_by_task(self, client, test_task):
        """GET /api/v2/comments?task_id=..."""
        response = client.get(f'/api/v2/comments?task_id={test_task.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_add_comment_api(self, auth_client, test_task):
        """POST /api/v2/comments добавляет комментарий."""
        response = auth_client.post('/api/v2/comments', json={
            'content': 'API комментарий',
            'task_id': test_task.id
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['content'] == 'API комментарий'


class TestStatisticsAPI:
    """Тесты API статистики."""

    def test_get_statistics(self, client):
        """GET /api/v2/statistics возвращает статистику."""
        response = client.get('/api/v2/statistics')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_users' in data
        assert 'total_tasks' in data