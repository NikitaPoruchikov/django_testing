from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class NoteLogicTests(TestCase):
    NEW_NOTE_TEXT = 'Текст новой заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = cls.create_user('author')
        cls.user = cls.create_user('auth_user')
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Тестовый текст', author=cls.author)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': 'Заголовок', 'text': cls.NEW_NOTE_TEXT}

    @staticmethod
    def create_user(username):
        return User.objects.create_user(
            username=username, password='password123')

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse('users:login'), response.url)

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(
            reverse('notes:add'), data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(title='Заголовок', text=self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.author, self.user)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Нельзя создать две заметки с одинаковым slug."""
        Note.objects.create(title='Заметка 1', text='Текст',
                            author=self.user, slug='duplicate-slug')
        duplicate_form_data = {'title': 'Заметка 2',
                               'text': 'Текст', 'slug': 'duplicate-slug'}
        response = self.auth_client.post(
            reverse('notes:add'), data=duplicate_form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(response, form='form', field='slug',
                             errors=WARNING)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Нельзя создать две заметки с одинаковым slug."""
        Note.objects.create(title='Заметка 1', text='Текст',
                            author=self.user, slug='duplicate-slug')
        duplicate_form_data = {'title': 'Заметка 2',
                               'text': 'Текст', 'slug': 'duplicate-slug'}
        response = self.auth_client.post(
            reverse('notes:add'), data=duplicate_form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        expected_error = f'duplicate-slug{WARNING}'
        self.assertFormError(response, form='form', field='slug',
                             errors=expected_error)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user1', password='12345')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок', text=cls.NOTE_TEXT, author=cls.user)
        cls.edit_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.delete_url = reverse('notes:delete', kwargs={
                                 'slug': cls.note.slug})
        cls.form_data = {'title': 'Заголовок', 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        """Авторизованный пользователь может удалять свои заметки."""
        response = self.auth_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cannot_delete_another_user_note(self):
        """Авторизованный пользователь не может удалять чужие заметки."""
        other_user = User.objects.create_user(
            username='user2', password='12345')
        other_client = Client()
        other_client.force_login(other_user)
        response = other_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_author_can_edit_note(self):
        """Авторизованный пользователь может редактировать свои заметки."""
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cannot_edit_another_user_note(self):
        """Авторизованный пользователь не может редактировать чужие заметки."""
        other_user = User.objects.create_user(
            username='user2', password='12345')
        other_client = Client()
        other_client.force_login(other_user)
        response = other_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
