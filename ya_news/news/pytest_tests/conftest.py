import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def create_news_user(db, user):
    """Создает новость с автором user."""
    return News.objects.create(title='Заголовок', text='Текст', author=user)


@pytest.fixture
def create_news(db):
    """
    Создает в базе данных серию новостей.
    Возвращает список созданных объектов новостей.
    """
    return News.objects.bulk_create([
        News(title=f'Новость {i}', text='Просто текст.') for i in range(10)
    ])


@pytest.fixture
def news_with_comments(db, create_news, user):
    """
    Создает одну новость с комментариями от пользователя.
    Использует первую новость, созданную фикстурой create_news.
    Возвращает пару (новость, пользователь), где новость содержит комментарии.
    """
    news_item = News.objects.first()
    Comment.objects.bulk_create([
        Comment(news=news_item, author=user,
                text=f'Комментарий {i}') for i in range(5)
    ])
    return news_item, user


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Фикстура для активации доступа к базе данных для всех тестов.
    Используется автоматически, не требует явного вызова.
    """
    pass


@pytest.fixture
def news():
    """Создает новость для тестов."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def user():
    """Создает пользователя для тестов."""
    return User.objects.create_user(username='Мимо Крокодил')


@pytest.fixture
def another_user():
    """Создает другого пользователя для тестов комментариев."""
    return User.objects.create_user(username='Читатель',
                                    password='another_strong_password')


@pytest.fixture
def comment(news, user):
    """Создает комментарий для тестов."""
    return Comment.objects.create(news=news,
                                  author=user, text='Текст комментария')


@pytest.fixture
def auth_client(client, user):
    """Авторизованный клиент для имитации действий пользователя в системе."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def another_auth_client(auth_client, another_user):
    """Авторизованный клиент для имитации действий другого пользователя."""
    auth_client = Client()
    auth_client.force_login(another_user)
    return auth_client


@pytest.fixture
def news_detail_url(news):
    """Возвращает URL для детального просмотра новости, требует объект news."""
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def comment_url(comment):
    """Возвращает URL для детального просмотра комментария, объект comment."""
    return reverse('news:comment', kwargs={'pk': comment.pk})


@pytest.fixture
def news_delete_url(comment):
    """Возвращает URL для удаления новости или комментария, объект comment."""
    return reverse('news:delete', kwargs={'pk': comment.id})


@pytest.fixture
def login_url():
    """Возвращает URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def news_edit_url(comment):
    """Возвращает URL для редактирования новости или комментария."""
    return reverse('news:edit', kwargs={'pk': comment.id})


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы новостей."""
    return reverse('news:home')


@pytest.fixture
def logout_url():
    """Возвращает URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Возвращает URL страницы регистрации."""
    return reverse('users:signup')
