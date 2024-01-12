from rest_framework import serializers
from .models import Clipboard, Image


# POST_Request
class PostClipboardRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    clipboard_id = serializers.IntegerField()
    url = serializers.URLField(max_length=2048)


# Response
class ImagesInnerDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'img_url', 'created_at', 'updated_at', 'deleted_at', 'favorite']


class ClipboardResponseSerializer(serializers.ModelSerializer):
    images_list = ImagesInnerDictSerializer(many=True, read_only=True, source='images')

    class Meta:
        model = Clipboard
        fields = ['id', 'images_list']

