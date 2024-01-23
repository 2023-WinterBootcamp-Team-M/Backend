
from django.db import models

from accountinfo.models import accountinfo


# Create your models here.


class BookmarkFolder(models.Model):
    user_id = models.ForeignKey(accountinfo,on_delete=models.CASCADE, db_constraint=False)
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
    icon = models.CharField(max_length=2048,
                            default="https://previews.123rf.com/images/salimcreative/salimcreative2005/salimcreative200500050/148346486-%EB%B6%81%EB%A7%88%ED%81%AC-%EC%95%84%EC%9D%B4%EC%BD%98.jpg")
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

class Reminder(models.Model):
    bookmark_name = models.CharField(max_length=20)
    bookmark_url = models.CharField(max_length=2048)
    user_id = models.ForeignKey(accountinfo,on_delete=models.CASCADE, db_constraint=False)
    is_checked = models.BooleanField(default=False)
    accumulated_days = models.IntegerField()