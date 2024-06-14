from http import HTTPStatus

from django.urls import reverse

from .common import CommonTestCase
from notes.forms import NoteForm


class TestHome(CommonTestCase):
    def test_notes_visibility_by_user(self):
        """Проверка видимости заметок пользователя."""
        test_cases = [
            (self.user1, self.notes_user1, True),
            (self.user2, self.notes_user1, False)
        ]
        for user, notes, should_see_notes in test_cases:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                visible_notes = set(
                    note.id for note in response.context['object_list'])
                expected_notes = set(note.id for note in notes)
                if should_see_notes:
                    self.assertTrue(expected_notes <= visible_notes,
                                    f"{user.username} should see their notes")
                else:
                    self.assertTrue(expected_notes.isdisjoint(visible_notes),
                                    f"{user.username} should not see")
                self.client.logout()

    def test_note_form_context(self):
        """Проверка, что формы создания и редактирования заметки,
        передаются в контексте и имеют правильный тип.
        """
        self.client.force_login(self.user1)

        # Тестирование страницы добавления заметки
        with self.subTest(msg="Testing add note form"):
            add_response = self.client.get(reverse('notes:add'))
            self.assertEqual(add_response.status_code, HTTPStatus.OK)
            self.assertIn('form', add_response.context)
            self.assertIsInstance(add_response.context['form'], NoteForm)

        # Тестирование страницы редактирования заметки
        with self.subTest(msg="Testing edit note form"):
            edit_response = self.client.get(
                reverse('notes:edit', kwargs={
                    'slug': self.notes_user1[0].slug}))
            self.assertEqual(edit_response.status_code, HTTPStatus.OK)
            self.assertIn('form', edit_response.context)
            self.assertIsInstance(edit_response.context['form'], NoteForm)
