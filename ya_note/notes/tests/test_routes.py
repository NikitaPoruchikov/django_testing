from http import HTTPStatus

from .common import CommonTestCase


class PublicPagesTests(CommonTestCase):
    def test_page_access(self):
        """Проверка доступа к страницам для различных пользователей."""
        public_pages = [
            self.home_url,
            self.login_url,
            self.logout_url,
        ]

        pages = [
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url(self.notes_user1[0].slug),
            self.edit_url(self.notes_user1[0].slug),
            self.delete_url(self.notes_user1[0].slug),
        ]
        # Проверка доступа к публичным страницам
        for url in public_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверка доступа к приватным страницам для залогиненного пользователя
        self.client.force_login(self.user1)
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверка редиректа анонимного пользователя на страницу логина
        self.client.logout()
        login_url = self.login_url
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f'{login_url}?next={url}')

    def test_note_edit_delete_access_restricted_to_author(self):
        """Проверка, что редактирование и удаление доступны только автору."""
        restricted_pages = [
            self.edit_url(self.notes_user1[0].slug),
            self.delete_url(self.notes_user1[0].slug),
        ]

        self.client.force_login(self.user2)
        for url in restricted_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
