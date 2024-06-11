from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestHomePageContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1', password='12345')
        cls.user2 = User.objects.create_user(
            username='user2', password='12345')
        cls.notes_user1 = [
            Note.objects.create(title=f'Test Note {i}', text='Test text',
                                author=cls.user1) for i in range(5)
        ]
        cls.notes_user2 = [
            Note.objects.create(title=f'Other Note {i}', text='Other text',
                                author=cls.user2) for i in range(5)
        ]

    def test_notes_in_object_list(self):
        """Проверка, что заметки user1 отображаются, а user2 - нет."""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        notes = response.context['object_list']
        for note in self.notes_user1:
            self.assertIn(note, notes)
        for note in self.notes_user2:
            self.assertNotIn(note, notes)

    def test_create_note_form_in_context(self):
        """Проверка, что форма создания заметки передается в контексте."""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_edit_note_form_in_context(self):
        """Проверка, форма редактирования заметки передается в контексте."""
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': self.notes_user1[0].slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
