from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description',
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        post = PostModelTest.post
        expected_group_str = group.title
        expected_post_str = post.text[:15]
        self.assertEqual(expected_group_str, str(group))
        self.assertEqual(expected_post_str, str(post))
