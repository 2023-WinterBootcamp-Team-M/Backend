from django.utils import timezone
from celery import shared_task
from .models import Bookmark
from datetime import timedelta
from rest_framework.response import Response

def send_alarm(thirty_days_ago):
    return Response({'message': f'북마크 추가 날짜 기준으로 {thirty_days_ago}일이 경과했습니다.'}, status=200)
@shared_task
def send_alarm_for_unread_bookmarks():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    bookmarks = Bookmark.objects.filter(is_connected=False, deleted_at__isnull=True)
    for bookmark in bookmarks:
        if bookmark.created_at < thirty_days_ago:
            bookmark.send_alarm(thirty_days_ago)
