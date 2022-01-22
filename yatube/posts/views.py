from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.NUM_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'posts': posts,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()
    paginator = Paginator(posts, settings.NUM_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post = author.posts.all()
    number_of_posts = author.posts.count()
    paginator = Paginator(post, settings.NUM_PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    following = Follow.objects.filter(
        user__username=request.user, author=author
    )
    context = {
        'page_obj': page_obj,
        'author': author,
        'number_of_posts': number_of_posts,
        'following': following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.all().count()
    form = CommentForm()
    comments = post.comments.all()
    title = str(post)
    context = {
        'post': post,
        'posts_count': posts_count,
        'title': title,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST' and form.is_valid():
        text = form.cleaned_data['text'],
        group = form.cleaned_data['group'],
        form.text = text
        form.group = group
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    else:
        context = {'form': form}
        return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'is_edit': is_edit,
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.NUM_PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', request.user)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_obj = Follow.objects.filter(author=author, user=request.user)
    if follow_obj.exists:
        follow_obj.delete()
    return redirect('posts:profile', request.user)
