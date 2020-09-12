"""project_IPTR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.HomePage.as_view(), name ='home'),
    path('resources',views.ResourceView.as_view(),name='resources'),
    path('tools/',include('app_tools.urls', namespace='tools')),
    path('secretpage/',views.SecretPage.as_view(), name='SecretPage'),
    path('',include('app_accounts_auth.urls')),
    path('forum/',include('app_forum.urls', namespace='app_forum')),
    path('', include('app_profiles.urls',namespace='app_profiles'))

]
