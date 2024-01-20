from rest_framework import serializers
from .models import Bookmark, BookmarkFolder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        fields = ['id', 'name', 'user_id', 'created_at', 'updated_at']

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'


# class get_BookmarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bookmark
#         fields = ['']
#
# class get_FolderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BookmarkFolder
#         fields = ['']


class FolderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        fields = ['id','user_id', 'name']

class BookmarkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'folder_id','name', 'url']

class BookmarkclassifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'name', 'url']

class move_BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'folder_id']
class update_delete_BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = []

class patch_delete_FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        fields = ['id', '']
# class delete_bookmarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bookmark
#         fields = ['deleted_at']
#
# class put_bookmarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bookmark
#         fields = ['name']

class update_delete_FolderSerializer (serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        fields = ['id', 'name']
class favorite_BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'name','url','icon']