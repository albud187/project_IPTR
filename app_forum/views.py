from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, PostComment
from django.contrib.auth.decorators import login_required

# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 20

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'app_forum/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/forum/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class UserPostListView(ListView):
    model = Post
    template_name = 'app_forum/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class UserPostCommentListView(ListView):
    model=Post
    template_name = 'app_forum/user_post_comments.html'
    context_object_name='posts'
    paginate_by=20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        AllUserCommentsList = PostComment.objects.filter(author=user)
        AllUserCommentsPostsList=[]

        for comment in AllUserCommentsList:
            AllUserCommentsPostsList.append(comment.post)

        AllUserPosts = Post.objects.filter(author=user)

        for post in AllUserPosts:
            if post not in AllUserCommentsPostsList:
                AllUserPosts.pop(post)

        return AllUserPosts.filter(author=user).first()





#### comments

class PostCommentDetailView(DetailView):
    model = PostComment

class PostCommentCreateView(LoginRequiredMixin, CreateView):
    model = PostComment
    fields = ['content']
    template_name = 'app_forum/post_comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs.get("pk"))
        return super().form_valid(form)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(PostComment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('app_forum:post_detail', pk=post_pk)

# class PostCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = PostComment
#     success_url = '/forum/'
#
#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == comment.author:
#             return True
#         return False

# class UserPostListView(ListView):
#     model = Post
#     template_name = 'app_forum/user_posts.html'  # <app>/<model>_<viewtype>.html
#     context_object_name = 'posts'
#     paginate_by = 5
#
#     def get_queryset(self):
#         user = get_object_or_404(User, username=self.kwargs.get('username'))
#         return Post.objects.filter(author=user).order_by('-date_posted')


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PostComment
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs.get("pk"))
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
