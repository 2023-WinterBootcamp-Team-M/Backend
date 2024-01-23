
from django.db import models
from django.core.exceptions import ValidationError
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

    def clean(self):
        # 부모의 clean 메서드 호출 (필수)
        super().clean()

        # 현재 북마크의 folder_id로부터 해당 폴더의 user_id 가져오기
        current_folder_user_id = self.folder_id.user_id

        # user_id가 같은 폴더들에서 중복된 url 또는 name을 확인
        duplicate_bookmarks = Bookmark.objects.filter(
            folder_id__user_id=current_folder_user_id,
            url=self.url,
            name=self.name,
            deleted_at__isnull=True  # 삭제되지 않은 북마크만 확인
        ).exclude(id=self.id)  # 현재 북마크는 제외

        if duplicate_bookmarks.exists():
            # 중복된 북마크가 존재하면 ValidationError 발생
            raise ValidationError("Duplicate bookmark found in the same user's folders.")

class Reminder(models.Model):
    bookmark_name = models.CharField(max_length=20)
    bookmark_url = models.CharField(max_length=2048)
    user_id = models.ForeignKey(accountinfo,on_delete=models.CASCADE, db_constraint=False)
    is_checked = models.BooleanField(default=False)
    accumulated_days = models.IntegerField()