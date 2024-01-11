from django.urls import path

from .views import *

urlpatterns = [
    path('Users', create_User, name='create_user'),
    path('folders', create_folder, name='create_folder'),
    path('folders/<int:folder_id>', delete_folder, name='delete_folder'),
    path('folders/name/<int:folder_id>', update_folder, name='update_folder'),
    path('Users/<int:user_id>/folders', get_folders, name='get_folders'),
    path('folders/<int:folder_id>/bookmarks', get_bookmarks_in_folder, name='get_bookmarks_in_folder'),
    path('bookmarks', create_bookmark, name='create_bookmark'),
    path('bookmarks/<int:folder_id>/<int:bookmark_id>', delete_bookmark, name='delete_bookmark'),
    path('folders/<int:folder_id>/<int:bookmark_id>', move_bookmark, name='move_bookmark'),
    path('folders/<int:folder_id>/bookmarks/<int:bookmark_id>', update_bookmark, name='update_bookmark'),
    path('bookmarks/favorite/<int:user_id>',favorite_bookmark_list,name='favorite_bookmark_list'),
    path('folders/bookmarks/favorite/<int:bookmark_id>', toggle_favorite_bookmark, name='toggle_favorite_bookmark'),



    #path('bookmarks/alarms?userId={user_id}',)
    # path('bookmarks', create_bookmark, name=''),
]