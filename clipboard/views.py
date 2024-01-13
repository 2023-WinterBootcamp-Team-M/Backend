from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from clipboard.models import *
from django.utils import timezone


class DeleteImagesView(APIView):
    @swagger_auto_schema(
        operation_description="클립보드 개별 이미지 삭제 API",
        operation_summary="클립보드 개별 이미지 지우기",
        tags=["Clipboard API"],
        operation_id="delete_images"
    )
    def delete(self, request, clipboard_id, image_id):
        queryset = Image.objects.filter(clipboard_id=clipboard_id, id=image_id)

        if not queryset.exists():
            return Response(
                {'message': '해당 이미지를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND)

        image = queryset.first()

        if image.deleted_at:
            return Response(
                {'message': '이미 삭제된 이미지입니다.'},
                status=status.HTTP_400_BAD_REQUEST)

        image.deleted_at = timezone.now()
        image.save()

        return Response({'message': '이미지 삭제 성공'},
                        status=status.HTTP_200_OK)
