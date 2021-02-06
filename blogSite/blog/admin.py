from django.contrib import admin

# Register your models her
from .models import Post, Comment

admin.site.register(Post)
admin.site.register(Comment)