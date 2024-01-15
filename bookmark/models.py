import uuid

from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)


class BookmarkFolder(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Bookmark(models.Model):
    name = models.CharField(max_length=20)
    #icon = models.ImageField(upload_to='bookmarks/')
    folder_id = models.ForeignKey(BookmarkFolder,on_delete=models.CASCADE)
    icon = models.CharField(max_length=2048)
    url = models.CharField(max_length=2048)
    is_connected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    favorite = models.BooleanField(default=False)
    short_summary = models.CharField(max_length=500, null=True)
    long_summary = models.CharField(max_length=1000, null=True)


    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)