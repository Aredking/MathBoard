"""
Тесты административной панели.
"""

import pytest
from app.models import User, Task, Comment
from app import db


class TestAdminAccess:
    """Тесты доступа к админ-панели."""

    def test_admin_dashboard_access(self, admin_client):
        """Администратор имеет доступ к дашборду."""
        response = admin_client.get('/admin/')
        assert response.status_code == 200
        assert b'Админ-панель' in response.data

    def test_admin_dashboard_denied_user(self, auth_client):
        """Обычный пользователь не имеет доступа."""
        response = auth_client.get('/admin/', follow_redirects=True)
        assert response.status_code == 403

    def test_admin_dashboard_denied_anonymous(self, client):
        """Анонимный пользователь перенаправляется."""
        response = client.get('/admin/', follow_redirects=True)
        assert b'Вход' in response.data

    def test_moderator_access(self, client, test_user, app):
        """Модератор имеет доступ."""
        with app.app_context():
            user = User.query.get(test_user.id)
            user.role = 'moderator'
            db.session.commit()
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'})
        response = client.get('/admin/')
        assert response.status_code == 200


class TestUserManagement:
    """Тесты управления пользователями."""

    def test_users_list(self, admin_client):
        """Список пользователей в админке."""
        response = admin_client.get('/admin/users')
        assert response.status_code == 200
        assert b'Управление пользователями' in response.data

    def test_edit_user(self, admin_client, test_user):
        """Редактирование пользователя."""
        response = admin_client.post(f'/admin/users/{test_user.id}/edit', data={
            'username': 'edited_user',
            'name': 'Edited Name',
            'role': 'moderator',
            'reputation': 100
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Пользователь обновлён' in response.data

    def test_toggle_user_active(self, admin_client, test_user, app):
        """Блокировка/разблокировка пользователя."""
        response = admin_client.post(f'/admin/users/{test_user.id}/toggle_active')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['is_active'] is False  # был True, стал False
        with app.app_context():
            user = User.query.get(test_user.id)
            assert not user.is_active

    def test_delete_user(self, admin_client, test_user, app):
        """Удаление пользователя."""
        # Создадим отдельного пользователя для удаления
        with app.app_context():
            victim = User(username='victim', name='Victim')
            victim.set_password('pass')
            db.session.add(victim)
            db.session.commit()
            victim_id = victim.id
        response = admin_client.post(f'/admin/users/{victim_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Пользователь удалён' in response.data
        with app.app_context():
            assert User.query.get(victim_id) is None


class TestTaskModeration:
    """Тесты модерации задач."""

    def test_tasks_list_moderation(self, admin_client):
        """Список задач в админке."""
        response = admin_client.get('/admin/tasks')
        assert response.status_code == 200
        assert b'Модерация задач' in response.data

    def test_moderate_task(self, admin_client, test_task, app):
        """Изменение статуса задачи."""
        response = admin_client.post(f'/admin/tasks/{test_task.id}/moderate', data={
            'status': 'archived'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Статус задачи обновлён' in response.data
        with app.app_context():
            task = Task.query.get(test_task.id)
            assert task.status == 'archived'


class TestCommentModeration:
    """Тесты модерации комментариев."""

    def test_comments_list(self, admin_client):
        """Список комментариев в админке."""
        response = admin_client.get('/admin/comments')
        assert response.status_code == 200
        assert b'Модерация комментариев' in response.data

    def test_toggle_comment_status(self, admin_client, test_task, test_user, app):
        """Скрытие/показ комментария."""
        with app.app_context():
            comment = Comment(content='Test', user_id=test_user.id, task_id=test_task.id)
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        response = admin_client.post(f'/admin/comments/{comment_id}/toggle_status')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'hidden'