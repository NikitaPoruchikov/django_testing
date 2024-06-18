from http import HTTPStatus

import pytest

# Определяем URL на уровне файла
HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
DETAIL_NEWS_URL = pytest.lazy_fixture('news_detail_url')
EDIT_COMMENT_URL = pytest.lazy_fixture('news_edit_url')
DELETE_COMMENT_URL = pytest.lazy_fixture('news_delete_url')

# Определяем клиентов на уровне файла
ANONYMOUS_CLIENT = pytest.lazy_fixture('anonymous_client')
AUTHOR_CLIENT = pytest.lazy_fixture('auth_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')

# Определяем параметры для тестов на уровне файла
URL_ACCESS_PARAMS = [
    (ANONYMOUS_CLIENT, HTTPStatus.OK, HOME_URL),
    (ANONYMOUS_CLIENT, HTTPStatus.OK, DETAIL_NEWS_URL),
    (ANONYMOUS_CLIENT, HTTPStatus.OK, LOGIN_URL),
    (ANONYMOUS_CLIENT, HTTPStatus.OK, LOGOUT_URL),
    (ANONYMOUS_CLIENT, HTTPStatus.OK, SIGNUP_URL),
    (AUTHOR_CLIENT, HTTPStatus.OK, DELETE_COMMENT_URL),
    (AUTHOR_CLIENT, HTTPStatus.OK, EDIT_COMMENT_URL),
    (NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND, DELETE_COMMENT_URL),
    (NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND, EDIT_COMMENT_URL),
]

REDIRECT_PARAMS = [
    (ANONYMOUS_CLIENT, DELETE_COMMENT_URL),
    (ANONYMOUS_CLIENT, EDIT_COMMENT_URL),
]


@pytest.mark.parametrize('client, status, url', URL_ACCESS_PARAMS)
def test_page_access(client, status, url):
    """Проверка доступа к страницам для различных пользователей."""
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize('client, url', REDIRECT_PARAMS)
def test_redirect_for_anonymous(client, url, login_url):
    """Проверка редиректа для анонимных пользователей на страницу логина."""
    expected_redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.url == expected_redirect_url
