from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


class CommonTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # URL-адреса
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

        # Пользователи
        cls.user1 = User.objects.create_user(
            username='testuser1', password='12345')
        cls.user2 = User.objects.create_user(
            username='testuser2', password='12345')

        # Создание заметок для каждого пользователя
        cls.notes_user1 = [
            Note.objects.create(title=f'User1 Note {i}',
                                text='Test text',
                                author=cls.user1) for i in range(5)
        ]
        cls.notes_user2 = [
            Note.objects.create(title=f'User2 Note {i}',
                                text='Test text',
                                author=cls.user2) for i in range(5)
        ]

        # Авторизованные клиенты
        cls.authenticated_client = cls.client_class()
        cls.authenticated_client.force_login(cls.user1)

        cls.another_authenticated_client = cls.client_class()
        cls.another_authenticated_client.force_login(cls.user2)

        # Общие данные для форм
        cls.form_data = {'title': 'Заголовок', 'text': 'Текст новой заметки',
                         'slug': 'new-slug'}

        # URL-адреса для деталей, редактирования и удаления
        cls.detail_url = lambda slug: reverse(
            'notes:detail', kwargs={'slug': slug})
        cls.edit_url = lambda slug: reverse(
            'notes:edit', kwargs={'slug': slug})
        cls.delete_url = lambda slug: reverse(
            'notes:delete', kwargs={'slug': slug})
