from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


INDEX = '/'
GROUP_LIST = '/group/test_group_slug/'
PROFILE = '/profile/test_user/'
CREATE = '/create/'
WRONG_URL = '/blablabla/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='test_title',
            slug='test_group_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )
        cls.POST = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.post.id])

        cls.templates_url_names = {
            INDEX: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            cls.POST: 'posts/post_detail.html',
            CREATE: 'posts/create_post.html',
            cls.POST_EDIT: 'posts/create_post.html',
            WRONG_URL: 'core/404.html'
        }

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template in PostURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_homepage(self):
        response = self.guest_client.get(INDEX)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls(self):
        """Проверка доступности страниц"""
        urls = {
            INDEX,
            GROUP_LIST,
            PROFILE,
            self.POST,
            CREATE,
            self.POST_EDIT,
        }
        for adress in urls:
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_guest(self):
        """Проверка доступности страниц для неавторизованного пользователя"""
        urls = {
            INDEX: HTTPStatus.OK.value,
            GROUP_LIST: HTTPStatus.OK.value,
            PROFILE: HTTPStatus.OK.value,
            self.POST: HTTPStatus.OK.value,
            CREATE: HTTPStatus.FOUND,
            self.POST_EDIT: HTTPStatus.FOUND,
        }
        for adress, expected in urls.items():
            with self.subTest(adress=adress):
                response = PostURLTests.guest_client.get(
                    adress
                )
                self.assertEqual(response.status_code, expected)
