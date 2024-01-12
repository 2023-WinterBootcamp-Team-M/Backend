from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
import requests
from bs4 import BeautifulSoup

from clipboard.models import *
from clipboard.serializers import (PostClipboardRequestSerializer,
                                   ClipboardResponseSerializer)
from rest_framework.generics import get_object_or_404
from django.utils import timezone


class PostClipboardView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="클립보드 이미지 크롤링 API",
        operation_summary="클립보드 이미지 크롤링",
        tags=["Clipboard API"],
        operation_id="clipboard_images_parsing",
        request_body=PostClipboardRequestSerializer,
        responses={200: ClipboardResponseSerializer()}
    )
    def post(self, request, *args, **kwargs):
        serializer = PostClipboardRequestSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            clipboard_id = serializer.validated_data['clipboard_id']
            req_url = serializer.validated_data['url']

            # 이미지 크롤링 + 저장
            try:
                # url에서 HTML 크롤링 + 파싱
                req = requests.get(req_url)
                soup = BeautifulSoup(req.content, 'html.parser')
                img_tags = soup.find_all('img', {'src': True})

                # Clipboard 모델에 request 된 clipboard_id 없으면 새로 create
                clipboard, created = Clipboard.objects.get_or_create(
                    id=clipboard_id,
                    user_id=user_id)

                # 파싱된 이미지 저장
                for img_tag in img_tags:
                    img_url = img_tag.get('src')
                    Image.objects.create(clipboard=clipboard, img_url=img_url)

                # Soft-delete : 50개 이상이면 가장 오래된 데이터 삭제
                max_items = 50
                current_items = Image.objects.filter(
                    clipboard_id=clipboard_id, deleted_at__isnull=True).count()

                if current_items > max_items:
                    oldest_items = Image.objects.filter(
                        clipboard_id=clipboard_id,
                        deleted_at__isnull=True
                        ).order_by('created_at')[:current_items - max_items]

                    # soft delete 진행
                    for item in oldest_items:
                        item.deleted_at = timezone.now()
                        item.save()

                # deleted_at이 null인 경우만 조회
                images = clipboard.images.filter(deleted_at__isnull=True)
                response_serializer = ClipboardResponseSerializer({'id': clipboard_id, 'images_list': images})

                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
