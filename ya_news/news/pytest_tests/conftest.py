import pytest

from django.contrib.auth import get_user_model

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def news(db):
    """Создает новость для тестов."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def user(db):
    """Создает пользователя для тестов."""
    return User.objects.create_user(username='Мимо Крокодил',
                                    password='strong_password')


@pytest.fixture
def another_user(db):
    """Создает другого пользователя для тестов комментариев."""
    return User.objects.create_user(username='Читатель',
                                    password='another_strong_password')


@pytest.fixture
def comment(db, news, user):
    """Создает комментарий для тестов."""
    return Comment.objects.create(news=news,
                                  author=user, text='Текст комментария')


@pytest.fixture
def auth_client(client, user):
    """Авторизованный клиент для имитации действий пользователя в системе."""
    client.force_login(user)
    return client


@pytest.fixture
def another_auth_client(client, another_user):
    """Авторизованный клиент для имитации действий другого пользователя."""
    client.force_login(another_user)
    return client
