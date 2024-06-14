from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture

from django.urls import reverse


@pytest.mark.parametrize("url", [
    lazy_fixture('home_url'),
    lazy_fixture('login_url'),
    lazy_fixture('logout_url'),
    lazy_fixture('signup_url')
])
def test_single_page_availability_for_anonymous_user(client, url):
    """Главная страница, cтраницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны анонимным пользователям.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page_for_anonymous_user(client, news_detail_url):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = news_detail_url
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_availability_for_comment_edit_and_delete(news_with_comments,
                                                  another_user, client):
    news, author = news_with_comments
    """Страницы удаления и редактирования комментария доступны
       автору комментария.
       Авторизованный пользователь не может зайти на страницы редактирования
       или удаления чужих комментариев (возвращается ошибка 404)."""
    statuses = {author: HTTPStatus.OK, another_user: HTTPStatus.NOT_FOUND}

    for user, status in statuses.items():
        client.force_login(user)
        for action in ['edit', 'delete']:
            url = reverse(f'news:{action}', kwargs={'pk': news.pk})
            response = client.get(url)
            assert response.status_code == status


@pytest.mark.parametrize(
    "url", [
        lazy_fixture('news_edit_url'),
        lazy_fixture('news_delete_url'),
    ])
def test_redirect_for_anonymous_client(client, url):
    """При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    expected_redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
