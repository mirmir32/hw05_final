from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


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

    def test_post_model_correct(self):
        group = PostModelTest.group
        post = PostModelTest.post
        expected_group_str = group.title
        expected_post_str = post.text[:15]
        self.assertEqual(expected_group_str, str(group))
        self.assertEqual(expected_post_str, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description',
        )

    def test_group_model_correct(self):
        group = GroupModelTest.group
        expected_group_str = group.title
        self.assertEqual(expected_group_str, str(group))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.user
        )
        cls.commentator = User.objects.create(username='test_user_commentator')
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.commentator,
            text='test_post'
        )

    def test_comment_modle_correct(self):
        comment = CommentModelTest.comment
        expected_comment_str = comment.text
        self.assertEqual(expected_comment_str, str(comment))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_user')
        cls.user = User.objects.create(username='test_user_commentator')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_follow_model_correct(self):
        follow = FollowModelTest.follow
        expected_object_name = f'{follow.user} подписан на {follow.author}'
        self.assertEqual(expected_object_name, str(follow))
