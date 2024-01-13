from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from clipboard.models import *
from django.utils import timezone


class DeleteAllImagesView(APIView):
    @swagger_auto_schema(
        operation_description="클립보드 비우기 API",
        operation_summary="클립보드 비우기",
        tags=["Clipboard API"],
        operation_id="delete_all_images"
    )
    def delete(self, request, clipboard_id):
        # soft-delete
        queryset = Image.objects.filter(clipboard_id=clipboard_id, deleted_at__isnull=True)
        for image in queryset:
            image.deleted_at = timezone.now()
            image.save()

        return Response(
            {'message': '클립보드 비우기 성공'},
            status=status.HTTP_200_OK)
