from django.db import models


class Clipboard(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class Image(models.Model):
    clipboard = models.ForeignKey(
        Clipboard,
        on_delete=models.CASCADE,
        related_name='images'
    )
    img_url = models.URLField(max_length=2048, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
    favorite = models.BooleanField(default=False)
