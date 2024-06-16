from http import HTTPStatus

import pytest


# Определяем URL на уровне файла
HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
COMMENT_EDIT_URL = pytest.lazy_fixture('news_edit_url')
COMMENT_DELETE_URL = pytest.lazy_fixture('news_delete_url')

# Определяем параметры для тестов на уровне файла
PUBLIC_URLS = [HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL, NEWS_DETAIL_URL]

EDIT_DELETE_ACCESS_PARAMS = [
    ('auth_client', COMMENT_EDIT_URL, HTTPStatus.OK),
    ('auth_client', COMMENT_DELETE_URL, HTTPStatus.OK),
    ('another_auth_client', COMMENT_EDIT_URL, HTTPStatus.NOT_FOUND),
    ('another_auth_client', COMMENT_DELETE_URL, HTTPStatus.NOT_FOUND),
    (None, COMMENT_EDIT_URL, HTTPStatus.FOUND),
    (None, COMMENT_DELETE_URL, HTTPStatus.FOUND),
]


@pytest.mark.parametrize("url", PUBLIC_URLS)
def test_public_pages_availability_for_anonymous_user(client, url):
    """Публичные страницы (главная, регистрация, вход, выход, новость)
    доступны анонимным пользователям.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("user_fixture, url_func, expected_status",
                         EDIT_DELETE_ACCESS_PARAMS)
def test_note_edit_delete_access(client, request, user_fixture,
                                 url_func, expected_status, login_url):
    """Проверка доступа к страницам редактирования и удаления комментария
    для различных пользователей.
    """
    if user_fixture:
        client = request.getfixturevalue(user_fixture)
    if user_fixture is None:
        expected_redirect_url = f'{login_url}?next={url_func}'
        response = client.get(url_func)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == expected_redirect_url
    else:
        response = client.get(url_func)
        assert response.status_code == expected_status
