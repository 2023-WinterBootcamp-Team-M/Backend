from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from clipboard.models import *
from clipboard.serializers import ClipboardResponseSerializer
from rest_framework.generics import get_object_or_404


class GetClipboardView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="클립보드 조회 API",
        operation_summary="클립보드 조회",
        tags=["Clipboard API"],
        operation_id="clipboard_list",
        responses={200: ClipboardResponseSerializer()}
    )
    def get(self, request, clipboard_id, **kwargs):
        clipboard = get_object_or_404(Clipboard, id=clipboard_id)

        # deleted_at이 null인 경우만 조회
        images = clipboard.images.filter(deleted_at__isnull=True)

        serializer = ClipboardResponseSerializer({'id': clipboard_id, 'images': images})
        return Response(serializer.data, status=status.HTTP_200_OK)
