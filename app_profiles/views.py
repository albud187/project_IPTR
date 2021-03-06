from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from app_forum.models import Post, PostComment

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile


users_without_profile = User.objects.filter(profile__isnull=True)
for user in users_without_profile:
    Profile.objects.create(user=user)

class PublicProfileView(TemplateView):

    template_name = 'user_profile_public.html'
    def get_queryset(self, request):
        user = get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))

        userObject = User.objects.filter(username=user)[0]
        email = userObject.email
        context['email'] = email

        profile = Profile.objects.filter(user=user)[0]
        aboutString = profile.about
        context['about'] = aboutString
        return context

class UserPostListView(ListView):
    model = Post
    template_name = 'user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class UserPostCommentListView(ListView):
    model=Post
    template_name = 'user_post_comments.html'
    context_object_name='posts'
    paginate_by=20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        AllUserComments = PostComment.objects.filter(author=user)
        AllUserCommentsPostList = []
        for comment in AllUserComments:
            AllUserCommentsPostList.append(comment.post)

        return list(dict.fromkeys(AllUserCommentsPostList))

@login_required
def profile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('app_profiles:profile')

    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'p_form': p_form
    }

    return render(request, 'user_profile_private.html', context)



# @login_required
# def profile(request):
#     if request.method == 'POST':
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#         p_form = ProfileUpdateForm(request.POST,
#                                    request.FILES,
#                                    instance=request.user.profile)
#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             messages.success(request, f'Your account has been updated!')
#             return redirect('app_profiles:profile')
#
#     else:
#         u_form = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=request.user.profile)
#
#     context = {
#         'u_form': u_form,
#         'p_form': p_form
#     }
#
#     return render(request, 'user_profile_private.html', context)
