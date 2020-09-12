from django.contrib import admin

# Register your models here.
from .models import Post, PostComment

admin.site.register(Post)
admin.site.register(PostComment)
