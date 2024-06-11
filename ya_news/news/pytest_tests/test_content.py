import pytest

from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User

from news.models import News, Comment


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def create_news(db):
    return News.objects.bulk_create([
        News(title=f'Новость {i}', text='Просто текст.') for i in range(10)
    ])


@pytest.fixture
def news_with_comments(db, create_news):
    news_item = News.objects.first()
    user = User.objects.create_user(
        username='Лев Толстой', password='password')
    Comment.objects.bulk_create([
        Comment(news=news_item,
                author=user, text=f'Комментарий {i}') for i in range(5)])

    return news_item, user


@pytest.mark.django_db
def test_news_count(client, home_url, create_news):
    """Проверка, что на главной отображается не более 10 новостей."""
    response = client.get(home_url)
    news_list = response.context.get(
        'object_list', response.context.get('news_list'))
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, home_url, create_news):
    """Проверка, что новости отсортированы от самых свежих к самым старым."""
    response = client.get(home_url)
    news_list = response.context.get(
        'object_list', response.context.get('news_list', []))
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news_with_comments):
    """Проверка, что комментарии отсортированы в хронологическом порядке."""
    news_item, _ = news_with_comments
    detail_url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = client.get(detail_url)
    comment_list = response.context.get(
        'comment_list', response.context.get('comments', []))
    dates = [comment.created for comment in comment_list]
    assert dates == sorted(dates)


@pytest.mark.django_db
def test_comment_form_visibility(client, news_with_comments):
    """Видимости формы комментов для аноним и авторизованного пользователя."""
    news_item, user = news_with_comments
    detail_url = reverse('news:detail', kwargs={'pk': news_item.pk})

    # Анонимный пользователь
    response = client.get(detail_url)
    assert 'form' not in response.context

    # Авторизованный пользователь
    client.force_login(user)
    response = client.get(detail_url)
    assert 'form' in response.context
