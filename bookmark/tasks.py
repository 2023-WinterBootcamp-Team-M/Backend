from django.utils import timezone
from datetime import timedelta, datetime

from accountinfo.models import accountoptions, accountinfo
from bookmark.models import Bookmark, BookmarkFolder, Reminder
from celery import Celery
from django_back.celery import logger
import time
from celery import shared_task


#hour=9, minute=0

@shared_task
def want_result():
    logger.info('Got Request - Starting work ')
    try:
        bookmarks = Bookmark.objects.filter(is_connected=False, deleted_at__isnull=True)
    except Bookmark.DoesNotExist:
        result = 15
        time.sleep(4)
        logger.info('Work Finished')
        return result

    for bookmark in bookmarks:
        user_id = bookmark.folder_id.user_id
        account_info = accountinfo.objects.get(id=user_id.id)  # 기본 키에 따라 수정
        user_options = accountoptions.objects.get(accountid=account_info.id)
        option = user_options.bookmarkalertoption
        alarm_option = 0

        if option == 0:
             alarm_option = timezone.now() - timedelta(days=15)
        elif option == 1:
             alarm_option = timezone.now() - timedelta(days=30)

        if bookmark.created_at < alarm_option: #bookmark.created_at < thirty_days_ago
            time_difference = timezone.now() - bookmark.created_at
            folder_user_id = bookmark.folder_id.user_id

            try:
                exist_reminder = Reminder.objects.get(bookmark_url=bookmark.url)
                exist_reminder.accumulated_days = time_difference.days
                exist_reminder.is_checked = False
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


