import pytest

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, {'text': 'A new comment'})
    assert response.status_code == 302
    assert '/login' in response.url
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(auth_client, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = auth_client.post(url, {'text': 'Valid comment'})
    assert response.status_code == 302
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_comment_with_bad_words_not_posted(auth_client, news):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    bad_words_data = {'text': f'Some text {BAD_WORDS[0]} another text'}
    response = auth_client.post(url, data=bad_words_data)
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_edit_own_comment(auth_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = auth_client.post(edit_url, {'text': 'Edited comment'})
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == 'Edited comment'


@pytest.mark.django_db
def test_user_can_delete_own_comment(auth_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = auth_client.delete(delete_url)
    assert response.status_code == 302
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another(another_auth_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = another_auth_client.delete(delete_url)
    assert response.status_code == 404
    assert Comment.objects.count() == 1
