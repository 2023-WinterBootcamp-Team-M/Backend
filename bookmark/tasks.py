from django.utils import timezone
from datetime import timedelta, datetime

from bookmark.models import Bookmark, BookmarkFolder, Reminder
from celery import Celery
from django_back.celery import logger
import time
from celery import shared_task


#hour=9, minute=0

@shared_task
def want_result():
    logger.info('Got Request - Starting work ')
    thirty_days_ago = timezone.now() - timedelta(days=30)
    try:
        bookmarks = Bookmark.objects.filter(is_connected=False, deleted_at__isnull=True)
    except Bookmark.DoesNotExist:
        result = 15
        time.sleep(4)
        logger.info('Work Finished')
        return result

    for bookmark in bookmarks:
        if bookmark.created_at > thirty_days_ago:
            time_difference = timezone.now() - bookmark.created_at
            folder_user_id = bookmark.folder_id.user_id

            try:
                exist_reminder = Reminder.objects.get(bookmark_url=bookmark.url)
                exist_reminder.accumulated_days = time_difference.days
                exist_reminder.save()
            except Reminder.DoesNotExist:
                reminder = Reminder(
                    bookmark_name=bookmark.name,
                    bookmark_url=bookmark.url,
                    user_id=folder_user_id,
                    accumulated_days=time_difference.days
                )
                reminder.save()

    return 12


