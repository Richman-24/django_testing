from django.test import Client

import pytest

from news.models import Comment, News

# Пользователи
@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')

@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')

# Клиенты
@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client

@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client

# Данные
@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст',
    )

@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        text='Комментарий',
        author=author
    )

@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}