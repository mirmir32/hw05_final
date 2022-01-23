import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

CREATE = reverse('posts:post_create')
PROFILE = reverse('posts:profile', kwargs={'username': 'test_author'})
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
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
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description',
        )
        cls.post = Post.objects.create(
            text='test_text',
            group=cls.group,
            author=cls.author,
        )
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.post.id])
        cls.POST_DETAIL = reverse('posts:post_detail', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        posts_count = Post.objects.count()

        form_data = {
            'text': 'test_text',
            'group': self.group.id,
            'username': self.author.username,
            'image': UPLOADED
        }

        response = self.authorized_author.post(
            CREATE,
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='test_text',
                author=self.author,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'post_id': self.post.id,
            'text': 'test_text_edit',
            'group': self.group.id,
            'author': self.author,
        }
        response = self.authorized_author.post(
            self.POST_EDIT,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, self.POST_DETAIL
        )
        edit_post = Post.objects.latest('id')
        self.assertEqual(edit_post.text, 'test_text_edit')
        self.assertEqual(edit_post.author, self.author)
        self.assertEqual(edit_post.group, self.group)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )
        cls.POST_DETAIL = reverse('posts:post_detail', args=[cls.post.id])
        cls.ADD_COMMENT = reverse('posts:add_comment', args={cls.post.pk})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_comment(self):
        """Комментарий создается на странице поста"""
        post = self.post
        comments_count = post.comments.count()
        form_data = {
            'text': 'Новый комментарий',
            'author': self.author,
        }
        response = self.authorized_author.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, self.POST_DETAIL
        )
        self.assertEqual(self.post.comments.count(), comments_count + 1)

        comment = Comment.objects.first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, form_data['author'])

    def test_guest_cant_create_comment(self):
        """Неавторизированный пользователь не может комментировать пост"""
        post = self.post
        comments_count = post.comments.count()
        form_data = {
            'text': 'Комментарий',
        }
        response = self.guest_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments_count)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse(
                'posts:add_comment',
                args={self.post.pk}
            )
        )
        self.assertFalse(
            Post.objects.filter(text=form_data['text'],).exists()
        )
