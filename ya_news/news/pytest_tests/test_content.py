import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, home_url, create_news):
    """Проверка, что на главной отображается не более 10 новостей."""
    response = client.get(home_url)
    news_list = response.context.get(
        'object_list', response.context.get('news_list'))
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url):
    """Проверка, что новости отсортированы от самых свежих к самым старым."""
    response = client.get(home_url)
    news_list = response.context.get(
        'object_list', response.context.get('news_list', []))
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, news_with_comments):
    """Проверка, что комментарии отсортированы в хронологическом порядке."""
    news_item, _ = news_with_comments
    detail_url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = client.get(detail_url)
    comment_list = response.context.get(
        'comment_list', response.context.get('comments', []))
    dates = [comment.created for comment in comment_list]
    assert dates == sorted(dates)


@pytest.mark.parametrize("client_fixture, form_visible", (
    ('client', False),        # Анонимный пользователь
    ('auth_client', True)     # Авторизованный пользователь
))
def test_comment_form_visibility(request, client_fixture,
                                 form_visible, news_detail_url):
    """Видимость формы комментов для аноним и авторизованного пользователя."""
    client = request.getfixturevalue(client_fixture)
    response = client.get(news_detail_url)
    assert ('form' in response.context) == form_visible
    if form_visible:
        assert isinstance(response.context['form'], CommentForm)
