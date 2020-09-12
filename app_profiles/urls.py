from django.urls import path
from . import views

app_name = 'app_profiles'

urlpatterns = [
    path('public_profile/<str:username>', views.PublicProfileView.as_view(), name='public_profile'),
    path('public_profile/<str:username>/posts', views.UserPostListView.as_view(), name='user_posts'),
    path('public_profile/<str:username>/posts_comments', views.UserPostCommentListView.as_view(), name='user_posts_comments')


    ]
