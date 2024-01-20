from django.db import models

# Create your models here.
class accountinfo(models.Model):
    user_name = models.CharField(max_length=20, null=False, blank=False)
    email = models.CharField(max_length=50, null=False, unique=True, blank=False)
    password = models.CharField(max_length=300, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)
    deleted_at = models.DateTimeField(null=True, default=None)

class accountoptions(models.Model):
    accountid = models.IntegerField(null=False, unique=True)
    summarizeoption = models.IntegerField(default=0)
    startupoption = models.IntegerField(default=0)
    bookmarkalertoption = models.IntegerField(default=1)
    themeoption = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=None, null=True)
    deleted_at = models.DateTimeField(default=None, null=True)