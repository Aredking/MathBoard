from requests import get, post
from sqlalchemy import delete

print(get('http://localhost:5000/api/v2/users').json())
print(get('http://localhost:5000/api/v2/users/1').json())  # запросы корректны

print(get('http://localhost:5000/api/v2/users/12421342142134').json())  # нет пользователя
print(get('http://localhost:5000/api/v2/users/sdfsdf').json())  # неправильный id

print(post('http://localhost:5000/api/v2/users', json={}).json())  # словарь отсутствует

print(delete('http://localhost:5000/api/v2/users/111').json())  # нет id = 111 в базе => удаление невозможно
