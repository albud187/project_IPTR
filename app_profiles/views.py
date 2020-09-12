from django.shortcuts import render
from django.views.generic import TemplateView, ListView
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from app_forum.models import Post, PostComment

class PublicProfileView(TemplateView):

    template_name = 'user_profile_public.html'
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))


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
    # paginate_by=20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        AllUserComments = PostComment.objects.filter(author=user)
        AllUserCommentsPostList = []
        for comment in AllUserComments:
            AllUserCommentsPostList.append(comment.post)

        AllPosts = Post.objects.all()
        AllPostsList = list(AllPosts)
        for post in AllPostsList:
            if post not in AllUserCommentsPostList:
                AllPostsList.remove(post)

        return AllPostsList
