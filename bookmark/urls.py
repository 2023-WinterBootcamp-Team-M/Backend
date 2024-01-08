from django.urls import path

from .views import *

app_name = ''
urlpatterns = [
    path('folders', create_folder, name=''),
    path('folders/{user_id}', get_folders, name=''),
    path('bookmarks/folder_id', get_bookmarks_in_folder, name=''),
    path('bookmarks', create_bookmark, name=''),
    path('folders/{folder_id}/bookmarks/{bookmarks_id}', update_bookmark, name=''),
    path('folders/{folder_id}/bookmarks/{bookmarks_id}', delete_bookmark, name=''),
    # path('bookmarks', , name=''),
    # path('bookmarks', create_bookmark, name=''),
]