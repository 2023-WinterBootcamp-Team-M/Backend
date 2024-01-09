from rest_framework import serializers
from .models import Bookmark, BookmarkFolder, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 어쨌든 필드의 값은 나중에 UserSerializer로 data를 간단하게 다룰 때 필요
        # 구글 소셜 로그인을 한다고 생각했을 때, 우리 DB로 그 내용을 옮긴다면
        # 이 3가지 필드 외에는 쓸 일이 없다고 생각 (생수삭은 제외해도 될듯)
        fields = ['id', 'name', 'email']

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        fields = '__all__'

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        # 북마크 필드는 folder_id(fk), url, icon, name, is_connected, 생수삭
        # 음 우선 folder_id가 필요할까? 나중에
        fields = '__all__'

class FolderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        fields = ['id','user_id', 'name']

class BookmarkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'folder_id','name', 'url', 'icon']

class put_delete_BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['folder_id','name', 'url', 'icon']
# class delete_bookmarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bookmark
#         fields = ['deleted_at']
#
# class put_bookmarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bookmark
#         fields = ['name']

