from http import HTTPStatus

from pytils.translit import slugify

from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

from .common import CommonTestCase


class NoteLogicTests(CommonTestCase):

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(reverse('notes:add'), {
                                    'title': 'New Note', 'text': 'New Text'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse('users:login'), response.url)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.authenticated_client.post(
            reverse('notes:add'), data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count + 1)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Нельзя создать две заметки с одинаковым slug."""
        Note.objects.create(title='Заметка 1', text='Текст',
                            author=self.user1, slug='duplicate-slug')
        duplicate_form_data = {'title': 'Заметка 2',
                               'text': 'Текст', 'slug': 'duplicate-slug'}
        response = self.authenticated_client.post(
            reverse('notes:add'), data=duplicate_form_data)
        expected_error = 'duplicate-slug' + WARNING
        self.assertFormError(response, 'form', 'slug', errors=[expected_error])

    def test_note_delete_by_author(self):
        """Автор может удалить свою заметку."""
        self.authenticated_client.force_login(self.user1)
        note_to_delete = self.notes_user1[0]
        response = self.authenticated_client.post(
            reverse('notes:delete', args=[note_to_delete.slug]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(
            slug=note_to_delete.slug).exists())

    def test_note_delete_by_other_user(self):
        """Другой пользователь не может удалить чужую заметку."""
        self.another_authenticated_client.force_login(self.user2)
        note_to_protect = self.notes_user1[0]
        response = self.another_authenticated_client.post(
            reverse('notes:delete', args=[note_to_protect.slug]))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(
            slug=note_to_protect.slug).exists())

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически с помощью функции pytils.translit.slugify.
        """
        self.client.force_login(self.user1)
        url = reverse('notes:add')
        data_without_slug = self.form_data.copy()
        del data_without_slug['slug']
        response = self.client.post(url, data_without_slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.latest('id')
        expected_slug = slugify(data_without_slug['title'])
        self.assertEqual(new_note.slug, expected_slug)
