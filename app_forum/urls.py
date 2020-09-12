from django.urls import path
from . import views

app_name = 'app_forum'

urlpatterns = [
    path('', views.PostListView.as_view(), name='forum_home'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comment/', views.PostCommentCreateView.as_view(), name='post_comment_create'),
    path('post/<int:pk>/comment/remove', views.comment_remove, name='post_comment_delete'),
    path('user/<str:username>', views.UserPostListView.as_view(), name='user_posts'),

]
