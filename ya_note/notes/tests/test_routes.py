from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user1', password='12345')
        cls.other_user = User.objects.create_user(
            username='user2', password='12345')
        cls.note = Note.objects.create(
            title='Test Note', text='Note text', author=cls.user)

    def test_public_pages_accessible_by_anyone(self):
        """Главная страница, логин и выход доступны всем пользователям."""
        public_pages = [
            reverse('notes:home'),
            reverse('users:login'),
            reverse('users:logout'),
        ]
        for url in public_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages_accessible_by_logged_in_user(self):
        """Приватные страницы доступны авторизованным пользователям."""
        private_pages = [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]
        self.client.force_login(self.user)
        for url in private_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirected_to_login(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        protected_pages = [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]
        login_url = reverse('users:login')
        for url in protected_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f'{login_url}?next={url}')

    def test_note_edit_access_restricted_to_author(self):
        """Проверка, что редактирование доступно только автору."""
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': self.note.slug}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_note_delete_access_restricted_to_author(self):
        """Проверка, что удаление доступно только автору."""
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse('notes:delete', kwargs={'slug': self.note.slug}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
