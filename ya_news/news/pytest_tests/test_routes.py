import pytest
from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def create_users(db):
    user1 = User.objects.create_user(username='Лев Толстой')
    user2 = User.objects.create_user(username='Читатель простой')
    return user1, user2


@pytest.fixture
def create_news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def create_comment(db, create_news, create_users):
    author, _ = create_users
    news_item = create_news
    return Comment.objects.create(
        news=news_item, author=author, text='Текст комментария'
    )


@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, create_news):
    """Проверка доступности страниц для анонимного пользователя."""
    urls = [
        reverse('news:home'),
        reverse('news:detail', kwargs={'pk': create_news.pk}),
        reverse('users:login'),
        reverse('users:logout'),
        reverse('users:signup')
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(create_comment, client):
    """Проверка доступа к редактированию и удалению комментария."""
    author, reader = create_comment.author, User.objects.create(
        username='Другой пользователь'
    )
    statuses = {author: HTTPStatus.OK, reader: HTTPStatus.NOT_FOUND}

    for user, status in statuses.items():
        client.force_login(user)
        for action in ['edit', 'delete']:
            url = reverse(f'news:{action}', kwargs={'pk': create_comment.pk})
            response = client.get(url)
            assert response.status_code == status


@pytest.mark.django_db
def test_redirect_for_anonymous_client(create_comment, client):
    """Проверка перенаправления анонимного пользователя на страницу логина."""
    login_url = reverse('users:login')
    for action in ['edit', 'delete']:
        url = reverse(f'news:{action}', kwargs={'pk': create_comment.pk})
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url


@pytest.mark.django_db
def test_registration_and_authentication_pages_accessibility(client):
    """Проверка доступности страниц регистрации для анонимных."""
    urls = [
        reverse('users:signup'),
        reverse('users:login'),
        reverse('users:logout')
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
