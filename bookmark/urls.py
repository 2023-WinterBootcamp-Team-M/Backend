from django.urls import path

from .views import *

urlpatterns = [
    path('folders', create_folder, name='create_folder'),
    path('folders/<int:user_id>', get_folders, name='get_folders'),
    path('bookmarks/<int:folder_id>', get_bookmarks_in_folder, name='get_bookmarks_in_folder'),
    path('bookmarks', create_bookmark, name='create_bookmark'),
    path('folders/<int:folder_id>/bookmarks/<int:bookmarks_id>', update_bookmark, name='update_bookmark'),
    path('bookmarks/<int:folder_id>/<int:bookmark_id>', delete_bookmark, name='delete_bookmark'),
    path('Users', create_User, name='create_user'),
    # path('bookmarks', create_bookmark, name=''),
]