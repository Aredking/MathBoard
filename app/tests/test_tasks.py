"""
Тесты функциональности задач: создание, редактирование, удаление,
проверка ответа, лайки, избранное.
"""

import pytest
from app.models import Task, Like, Favorite
from app import db


class TestTaskCRUD:
    """Тесты CRUD операций с задачами."""

    def test_index_page(self, client):
        """Главная страница доступна."""
        response = client.get('/')
        assert response.status_code == 200

    def test_task_detail(self, client, test_task):
        """Страница задачи доступна."""
        response = client.get(f'/task/{test_task.id}')
        assert response.status_code == 200
        assert b'Тестовая задача' in response.data

    def test_create_task(self, auth_client, app):
        """Создание новой задачи."""
        with app.app_context():
            from app.models import Category
            cat = Category.query.first()
            response = auth_client.post('/create', data={
                'title': 'Новая задача',
                'answer': '100',
                'difficulty': 'medium',
                'category': cat.id if cat else '',
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'Новая задача' in response.data
            task = Task.query.filter_by(title='Новая задача').first()
            assert task is not None
            assert task.answer == '100'

    def test_create_task_requires_login(self, client):
        """Неавторизованный пользователь не может создать задачу."""
        response = client.get('/create', follow_redirects=True)
        assert b'Вход' in response.data

    def test_edit_task_owner(self, auth_client, test_task):
        """Автор может редактировать задачу."""
        response = auth_client.post(f'/edit/{test_task.id}', data={
            'title': 'Обновлённая задача',
            'answer': '43',
            'difficulty': 'hard',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Обновлённая задача' in response.data

    def test_edit_task_not_owner(self, client, test_task, test_user):
        """Не автор не может редактировать задачу (403)."""
        # Создаём другого пользователя и логинимся
        from app import db
        from app.models import User
        with client.application.app_context():
            other = User(username='other', name='Other')
            other.set_password('pass')
            db.session.add(other)
            db.session.commit()
        client.post('/auth/login', data={'username': 'other', 'password': 'pass'})
        response = client.get(f'/edit/{test_task.id}')
        assert response.status_code == 403

    def test_delete_task_owner(self, auth_client, test_task, app):
        """Автор может удалить задачу."""
        response = auth_client.post(f'/delete/{test_task.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Задача удалена' in response.data
        with app.app_context():
            task = Task.query.get(test_task.id)
            assert task is None

    def test_delete_task_not_owner(self, client, test_task):
        """Не автор не может удалить задачу."""
        client.post('/auth/login',
                    data={'username': 'admin', 'password': 'adminpass'})  # админ может, но проверим обычного
        # Создадим обычного пользователя
        response = client.post('/auth/register', data={
            'username': 'user2', 'name': 'User2', 'password': 'pass', 'password2': 'pass'
        })
        client.post('/auth/login', data={'username': 'user2', 'password': 'pass'})
        response = client.post(f'/delete/{test_task.id}', follow_redirects=True)
        assert response.status_code == 403


class TestTaskInteractions:
    """Тесты взаимодействия с задачами: проверка ответа, лайки, избранное."""

    def test_check_answer_correct(self, auth_client, test_task, app):
        """Проверка правильного ответа."""
        response = auth_client.post(f'/check_answer/{test_task.id}', data={
            'answer': '42',
            'task_id': test_task.id
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'correct'
        with app.app_context():
            task = Task.query.get(test_task.id)
            assert task.solves_count == 1

    def test_check_answer_wrong(self, auth_client, test_task):
        """Проверка неправильного ответа."""
        response = auth_client.post(f'/check_answer/{test_task.id}', data={
            'answer': '43',
            'task_id': test_task.id
        })
        json_data = response.get_json()
        assert json_data['status'] == 'wrong'

    def test_like_task(self, auth_client, test_task, app):
        """Лайк задачи."""
        response = auth_client.post(f'/like/{test_task.id}')
        json_data = response.get_json()
        assert json_data['liked'] is True
        assert json_data['count'] == 1
        with app.app_context():
            like = Like.query.filter_by(user_id=1, task_id=test_task.id).first()
            assert like is not None

    def test_unlike_task(self, auth_client, test_task, app):
        """Снятие лайка."""
        # Сначала лайкаем
        auth_client.post(f'/like/{test_task.id}')
        response = auth_client.post(f'/like/{test_task.id}')
        json_data = response.get_json()
        assert json_data['liked'] is False
        assert json_data['count'] == 0
        with app.app_context():
            like = Like.query.filter_by(user_id=1, task_id=test_task.id).first()
            assert like is None

    def test_favorite_task(self, auth_client, test_task, app):
        """Добавление в избранное."""
        response = auth_client.post(f'/favorite/{test_task.id}')
        json_data = response.get_json()
        assert json_data['favorited'] is True
        with app.app_context():
            fav = Favorite.query.filter_by(user_id=1, task_id=test_task.id).first()
            assert fav is not None

    def test_unfavorite_task(self, auth_client, test_task, app):
        """Удаление из избранного."""
        auth_client.post(f'/favorite/{test_task.id}')
        response = auth_client.post(f'/favorite/{test_task.id}')
        json_data = response.get_json()
        assert json_data['favorited'] is False
        with app.app_context():
            fav = Favorite.query.filter_by(user_id=1, task_id=test_task.id).first()
            assert fav is None