from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .constant import TEXT_COMMENT

def test_comment_not_added_by_anonymous_user(client,
                                             news_detail_url):
    """Анонимный пользователь не может добавить комментарий."""
    initial_count = Comment.objects.count()
    client.post(news_detail_url, data=TEXT_COMMENT)
    assert Comment.objects.count() == initial_count


def test_authenticated_user_can_post_comment(auth_client,
                                             news_detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    initial_comment_count = Comment.objects.count()
    response = auth_client.post(news_detail_url, TEXT_COMMENT)
    assert response.status_code == HTTPStatus.FOUND  # 302
    assert Comment.objects.count() == initial_comment_count + 1


def test_comment_with_bad_words_not_posted(auth_client, news_detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    bad_words_data = {'text': f'Немного текста {BAD_WORDS[0]} другой текст'}
    initial_comment_count = Comment.objects.count()
    response = auth_client.post(news_detail_url, data=bad_words_data)
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == initial_comment_count


def test_user_can_edit_own_comment(auth_client,
                                   news_edit_url, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = auth_client.post(news_edit_url, TEXT_COMMENT)
    assert response.status_code == HTTPStatus.FOUND  # 302
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


def test_user_can_delete_own_comment(auth_client, news_delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    initial_comment_count = Comment.objects.count()
    response = auth_client.delete(news_delete_url)
    assert response.status_code == HTTPStatus.FOUND  # 302
    assert Comment.objects.count() == initial_comment_count - 1


def test_user_cant_delete_comment_of_another(another_auth_client,
                                             news_delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    initial_comment_count = Comment.objects.count()
    response = another_auth_client.delete(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND  # 404
    assert Comment.objects.count() == initial_comment_count
