from django.urls import path

from .views import *

urlpatterns = [

    path('folders', create_folder, name='create_folder'),
    path('folders/<int:folder_id>', update_delete_folder, name='update_delete_folder'),
    path('folders/list/<int:user_id>', get_folders, name='get_folders'),

    path('bookmarks', create_bookmark, name='create_bookmark'),
    path('bookmarks/summary/<int:bookmark_id>',get_bookmarks_summary, name='get_bookmarks_summary'),
    path('bookmarks/list/<int:user_id>', create_classify_bookmark, name='create_classify_bookmark'),
    path('bookmarks/<int:folder_id>', get_bookmarks_in_folder, name='get_bookmarks_in_folder'),
    path('bookmarks/<int:folder_id>/<int:bookmark_id>', update_delete_bookmark, name='update_delete_bookmark'),
    path('bookmarks/folders/<int:folder_id>/<int:bookmark_id>', move_bookmark, name='move_bookmark'),

    path('favorite/bookmarks/<int:user_id>',favorite_bookmark_list,name='favorite_bookmark_list'),
    path('favorite/<int:bookmark_id>', toggle_favorite_bookmark, name='toggle_favorite_bookmark'),

    #path('bookmarks/alarms?userId={user_id}',)
    # path('bookmarks', create_bookmark, name=''),
]