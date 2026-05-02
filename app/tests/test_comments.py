"""
Тесты комментариев: добавление, удаление, ответы.
"""

import pytest
from app.models import Comment, Task
from app import db


class TestComments:
    """Тесты комментариев."""

    def test_add_comment(self, auth_client, test_task, app):
        """Добавление комментария."""
        response = auth_client.post('/comments/add', data={
            'content': 'Отличная задача!',
            'task_id': test_task.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Отличная задача!' in response.data
        with app.app_context():
            comment = Comment.query.filter_by(content='Отличная задача!').first()
            assert comment is not None
            task = Task.query.get(test_task.id)
            assert task.comments_count == 1

    def test_add_comment_requires_login(self, client, test_task):
        """Неавторизованный не может комментировать."""
        response = client.post('/comments/add', data={
            'content': 'Спам',
            'task_id': test_task.id
        }, follow_redirects=True)
        assert b'Вход' in response.data

    def test_delete_comment_owner(self, auth_client, test_task, test_user, app):
        """Автор может удалить свой комментарий."""
        with app.app_context():
            comment = Comment(content='Мой коммент', user_id=test_user.id, task_id=test_task.id)
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        response = auth_client.post(f'/comments/delete/{comment_id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Комментарий удалён' in response.data
        with app.app_context():
            assert Comment.query.get(comment_id) is None

    def test_delete_comment_not_owner(self, client, test_task, test_user, app):
        """Не автор не может удалить чужой комментарий."""
        # Создаём комментарий от test_user
        with app.app_context():
            comment = Comment(content='Чужой коммент', user_id=test_user.id, task_id=test_task.id)
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        # Логинимся другим пользователем
        client.post('/auth/register', data={
            'username': 'hacker', 'name': 'Hacker', 'password': 'pass', 'password2': 'pass'
        })
        client.post('/auth/login', data={'username': 'hacker', 'password': 'pass'})
        response = client.post(f'/comments/delete/{comment_id}')
        assert response.status_code == 403

    def test_reply_to_comment(self, auth_client, test_task, test_user, app):
        """Ответ на комментарий."""
        with app.app_context():
            parent = Comment(content='Вопрос', user_id=test_user.id, task_id=test_task.id)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id
        response = auth_client.post(f'/comments/reply/{parent_id}', data={
            'content': 'Ответ на вопрос'
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['comment']['content'] == 'Ответ на вопрос'