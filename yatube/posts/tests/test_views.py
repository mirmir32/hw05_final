import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
INDEX = reverse('posts:index')
GROUP_LIST = reverse('posts:group_list', kwargs={'slug': 'test_group_slug'})
NEW_GROUP_LIST = reverse('posts:group_list', args=['test_new_group'])
PROFILE = reverse('posts:profile', kwargs={'username': 'test_author'})
CREATE = reverse('posts:post_create')
FOLLOW_INDEX = reverse('posts:follow_index')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
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
            description='test_descrioption'
        )

        cls.post = Post.objects.create(
            text='test_text',
            group=cls.group,
            author=cls.author,
            image=UPLOADED,
        )
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.post.id])
        cls.POST_DETAIL = reverse('posts:post_detail', args=[cls.post.id])

        cls.templates_pages_names = {
            INDEX: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            cls.POST_DETAIL: 'posts/post_detail.html',
            CREATE: 'posts/create_post.html',
            cls.POST_EDIT: 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL адресс использует соответствующий шаблон"""
        for reverse_name, template in (
            PostViewsTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTests.authorized_author.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)

    def check_post(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.author)
        self.assertTrue(post.image, self.post.image)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = PostViewsTests.authorized_client.get(INDEX)
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = PostViewsTests.authorized_client.get(GROUP_LIST)
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(PROFILE)
        post = response.context['page_obj'][0]
        self.check_post(post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(self.POST_DETAIL)
        post = response.context['post']
        self.check_post(post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = PostViewsTests.authorized_author.get(self.POST_EDIT)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_on_pages(self):
        """Новый пост отображается на нужных страницах"""
        self.new_group = Group.objects.create(
            title='test_new_group',
            slug='test_new_slug',
            description='test_new_description',
        )
        self.new_post = Post.objects.create(
            text='test_text',
            group=self.new_group,
            author=self.author,
        )
        self.PROFILE_NEW = reverse('posts:profile', args=[self.author])
        self.GROUP_LIST_NEW = reverse('posts:group_list',
                                      args=[self.group.slug])
        form_data = {
            'text': 'test_text',
            'group': 'test_new_group',
        }
        response = self.authorized_author.post(
            INDEX,
            data=form_data,
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'test_text')

        response = self.authorized_author.post(
            NEW_GROUP_LIST,
            data=form_data,
        )
        self.assertEqual(first_post.text, 'test_text')

        response = self.authorized_author.post(
            self.PROFILE_NEW,
            data=form_data,
        )
        self.assertEqual(first_post.text, 'test_text')

        response = self.authorized_client.get(
            self.GROUP_LIST_NEW
        )
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertEqual(post_text, 'test_text')

    def test_cache_index_page(self):
        """Тест кэша"""
        response = self.authorized_author.get(INDEX)
        content = response.content
        Post.objects.create(
            text='Тестовый пост',
            author=self.author,
        )
        response = self.authorized_author.get(INDEX)
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.authorized_author.get(INDEX)
        self.assertNotEqual(content, response.content)


class PaginatorViewsTest(TestCase):
    """Тест Paginator"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='test_author',
        )
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_description',
        )
        for i in range(13):
            Post.objects.create(
                text=f'Пост № {i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        posts_on_first_page = settings.NUM_PAGES
        posts_on_second_page = 3
        urls = [
            INDEX,
            GROUP_LIST,
            PROFILE
        ]
        for reverse_ in urls:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_).context.get('page_obj')),
                    posts_on_first_page
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    posts_on_second_page
                )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.follower = User.objects.create_user(username='test_follower')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

    def test_follow(self):
        """Авторизованный пользователь может подписаться на автора"""
        self.FOLLOW = reverse(
            'posts:profile_follow',
            args={self.author.username}
        )
        self.authorized_follower.get(self.FOLLOW)
        follow_count = Follow.objects.filter(
            user=self.follower.id,
            author=self.author.id
        ).count()
        self.assertEqual(follow_count, 1)

    def test_unfollow(self):
        """Авторизованный пользователь может отписаться от автора"""
        Follow.objects.create(user=self.follower, author=self.author)
        self.UNFOLLOW = reverse(
            'posts:profile_unfollow',
            args={self.author.username}
        )
        self.authorized_follower.get(self.UNFOLLOW)
        follow_count = Follow.objects.filter(
            user=self.follower.id,
            author=self.author.id
        ).count()
        self.assertEqual(follow_count, 0)

    def test_post_in_follower_index(self):
        """Новая запись автора появляется в ленте подписчиков"""
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.author
        )
        Follow.objects.create(user=self.follower, author=self.author)
        response = self.authorized_follower.get(FOLLOW_INDEX)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, post.text)

    def test_post_not_in_user_index(self):
        """Новая запись автора не появляется
        в ленте неподписанных пользователей
        """
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.author
        )
        Follow.objects.create(user=self.follower, author=self.author)
        user = User.objects.create_user(username='test_user')
        authorized_user = Client()
        authorized_user.force_login(user)
        response = authorized_user.get(FOLLOW_INDEX)
        posts = response.context['page_obj']
        self.assertNotIn(post, posts)
