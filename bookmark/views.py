from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from bookmark.models import *
from rest_framework import serializers
from bookmark.serializer import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.db.models import Prefetch
@swagger_auto_schema(method='post', request_body=UserSerializer)
# Create your views here.
@api_view(['POST'])
def create_User(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 폴더 생성 API
# 수정 필요
@swagger_auto_schema(method = "post", request_body = FolderSerializer)
@api_view(['POST'])
def create_folder(request):
    data = request.data
    serializer = FolderSerializer(data=data)

    # 폴더 이름 중복 처리
    if BookmarkFolder.objects.filter(name= data['name'], deleted_at__isnull=True).exists():
        return Response('The folder already exists', status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    return Response(serializer.errors,
        status=status.HTTP_400_BAD_REQUEST)


# 폴더 조회 API
# 북마크 폴더 리스트 조회(사용자가 북마크 패널 사용 시 처음 보게 되는 화면)
# chrome.bookmark API가 DRF에 어떤 식으로 값을 던지는 지 알아야 함.
# 오히려 user_id를 fk로 참조하는게 나을수도 있음 -> 일단 지금 현재는 괜찮긴 함
@swagger_auto_schema(method = "get", response_body = FolderSerializer)
@api_view(['GET'])
def get_folders(request, user_id):
    try:
        folders = BookmarkFolder.objects.filter(user_id=user_id, deleted_at__isnull=True)
        serializer = FolderSerializer(folders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except BookmarkFolder.DoesNotExist:
        return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)


# 폴더 내의 북마크 리스트 조회임
# folder_id는 다 따로임. 유저별 중복이 발생하지 X
# 여기서 중요한게 folder_id를 fk로 참조하고 있기 때문에 폴더가 같으면 fk도 같음
@swagger_auto_schema(method = "get", response_body = BookmarkSerializer)
@api_view(['GET'])
def get_bookmarks_in_folder(request, folder_id):
    try:
        # 폴더 조회
        bookmarks = Bookmark.objects.filter(folder_id=folder_id, deleted_at__isnull=True)

        serializer = BookmarkSerializer(bookmarks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except BookmarkFolder.DoesNotExist:
        return Response({'error': 'Folder not found.'}, status=status.HTTP_404_NOT_FOUND)


# 북마크 생성 API
# 크롬북마크 API -> DRF -> Open ai API -> 북마크 분류 API
# api 가 던져준 북마크 name에 넣어져야 함
@swagger_auto_schema(method='post',request_body=BookmarkSerializer)
@api_view(['POST'])
def create_bookmark(request):
    data = request.data
    # url하고 이름은 클라이언트가 지정하는 걸로 결정
    url = data.get('url')
    name = data.get('name')


    if Bookmark.objects.filter(url=url, deleted_at__isnull=True).exists():
        return Response({'error': 'Bookmark with the same URL already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    if Bookmark.objects.filter(name=name, deleted_at__isnull=True).exists():
        return Response({'error': 'Bookmark with the same name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = BookmarkSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 북마크 삭제 API
# 일단 우리가 아는 삭제가 아님 -> 기술적 삭제임 즉 deleted_at이 NULL이 아님.
# 삭제했던 것을 다시 부활시키면 Null로 해줘
@swagger_auto_schema(method='delete', response_body=BookmarkSerializer)
@api_view(['DELETE'])
def delete_bookmark(request, folder_id, bookmark_id):
    try:
        # 폴더와 북마크 조회
        bookmark = Bookmark.objects.get(pk=bookmark_id, folder_id=folder_id)

        # 기술적 삭제
        if bookmark.deleted_at is None:
            # 삭제되지 않은 경우에만 처리
            bookmark.deleted_at = timezone.now()
            bookmark.save()

            serializers = BookmarkSerializer(bookmark)

            return Response(serializers.data, status=status.HTTP_200_OK)
        else:
            return Response({'error: 이미 삭제된 북마크입니다'}, status=status.HTTP_400_BAD_REQUEST)

    except BookmarkFolder.DoesNotExist:
        return Response({'error': 'Folder not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Bookmark.DoesNotExist:
        return Response({'error': 'Bookmark not found.'}, status=status.HTTP_404_NOT_FOUND)

# 북마크 수정 API
# 왜 있어야 할까?
# -> 만약 gpt가 연관성 없는 북마크들을 따로 기타 북마크로 모았는데, 그게 바뀌면 수정되야 함
# -> 이걸 고려하면 PUT이 맞을 수도 있을 것 같음.
# @swagger_auto_schema(method='patch',request_body= BookmarkSerializer)
# @api_view(['PATCH'])
# def update_bookmark(request, folder_id, bookmark_id):
#     # 넘겨준 폴더 아이디, 북마크 아이디를 토대로
#     # 기존에 DB에 등록된 A폴더, 그리고 그 폴더의 a북마크를 서치
#
#     folder = BookmarkFolder.objects.get(pk=folder_id)
#     bookmark = Bookmark.objects.get(pk=bookmark_id, folder_id=folder_id)
#
#     # request data from client
#     data = request.data
#     # 클라이언트에게 받은 데이터의 폴더 아이디 부분을 기존의 폴더 아이디에 저장
#     # 즉 북마크 이동의 역할을 대신함
#     # folder.id = data['folder_id']
#
#     serializer = BookmarkSerializer(instance=bookmark, data=data, partial=True)
#
#     if serializer.is_valid():
#         new_url = serializer.validated_data.get('url', bookmark.url)
#         new_name = serializer.validated_data.get('name', bookmark.name)
#
#         # URL과 name이 기존에 등록된 DB의 다른 북마크들과 겹치지 않도록 함
#         if Bookmark.objects.filter(folder_id=folder, url=new_url).exclude(pk=bookmark.id).exists():
#             return Response({'error': 'Bookmark with the same URL already exists in the folder.'}, status=status.HTTP_400_BAD_REQUEST)
#         if Bookmark.objects.filter(folder_id=folder, name=new_name).exclude(pk=bookmark.id).exists():
#             return Response({'error': 'Bookmark with the same name already exists in the folder.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         # 바뀌었어야 저장하는 의미가 있으니
#         # 조건문을 거쳐 둘 중 하나라도 바뀌었으면 저장하도록 함
#         if new_url != bookmark.url or new_name != bookmark.name:
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'No changes to save'}, status=status.HTTP_304_NOT_MODIFIED)
#
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#

# 북마크 폴더 이동 함수
@swagger_auto_schema(method='patch', request_body=move_BookmarkSerializer)
@api_view(['PATCH'])
def move_bookmark(request, folder_id, bookmark_id):
    try:
        # url folder_id를 기준으로 만든 폴더(옮길 폴더)
        folder = BookmarkFolder.objects.get(id=folder_id)

        # url 정보로 얻은 옮길 북마크
        bookmark = Bookmark.objects.get(id=bookmark_id)  # 수정: bookmark_id로 북마크를 가져오도록 수정


        bookmark.folder_id = folder

        # 수정: Serializer 인스턴스 생성 시 인자로 instance와 data를 함께 전달
        serializer = BookmarkSerializer(instance=bookmark, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 수정: 유효성 검사 실패 시 에러 응답
    except (Bookmark.DoesNotExist, BookmarkFolder.DoesNotExist):
        return Response({'error': 'Bookmark or Folder not found'}, status=status.HTTP_404_NOT_FOUND)


# 북마크 이름, url을 수정할 수 있는 함수
@swagger_auto_schema(method = "patch", request_body=update_delete_BookmarkSerializer)
@api_view(['PATCH'])
def update_bookmark(request, folder_id, bookmark_id):
    try:
        # 기존 북마크 가져오기
        bookmark = Bookmark.objects.get(id=bookmark_id)

        # Serializer를 사용하여 데이터 유효성 검사 및 업데이트
        serializer = BookmarkSerializer(bookmark, data=request.data, partial=True)

        if serializer.is_valid():
            new_url = serializer.validated_data.get('url', bookmark.url)
            new_name = serializer.validated_data.get('name', bookmark.name)

            # 기존과 동일한 'url' 또는 'name'을 가진 다른 북마크가 있는지 확인
            if Bookmark.objects.filter(folder_id=folder_id, url=new_url, deleted_at__isnull=True).exclude(id=bookmark.id).exists():
                return Response({'error': 'This URL is already associated with another bookmark in the same folder.'}, status=status.HTTP_400_BAD_REQUEST)

            if Bookmark.objects.filter(folder_id=folder_id, name=new_name, deleted_at__isnull=True).exclude(id=bookmark.id).exists():
                return Response({'error': 'This name is already associated with another bookmark in the same folder.'}, status=status.HTTP_400_BAD_REQUEST)

            # 유효성 검사를 통과하고 중복이 없으면 저장
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Bookmark.DoesNotExist:
        return Response({'error': 'Bookmark not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(method='PATCH', request_body=FolderSerializer)
@api_view(['PATCH'])
def update_folder(request, folder_id):
    try:
        folder = BookmarkFolder.objects.get(id=folder_id)
        new_name = request.data.get('new_name', folder.name)

        folder.name = new_name
        folder.updated_at = timezone.now()
        folder.save()

        return Response({'id' : folder.id,
                         'name': folder.name
                         }, status=status.HTTP_200_OK)

    except BookmarkFolder.DoesNotExist:
        return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(method='DELETE', response_body='Success')
@api_view(['DELETE'])
def delete_folder(request, folder_id):
    try:
        folder = BookmarkFolder.objects.get(id=folder_id)
        if folder.deleted_at is None:
            # 폴더 삭제 시 해당 폴더에 속한 모든 북마크도 함께 삭제
            Bookmark.objects.filter(folder_id=folder_id).update(deleted_at=timezone.now())

            folder.deleted_at = timezone.now()
            folder.save()

            return Response({'message': 'Folder and associated bookmarks deleted successfully'},
                                status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Folder already deleted'}, status=status.HTTP_400_BAD_REQUEST)

    except BookmarkFolder.DoesNotExist:
        return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)






@swagger_auto_schema(method = "get", response_body=BookmarkSerializer)
@api_view(['GET'])
def favorite_bookmark_list(request,user_id):
    try:
        folders = BookmarkFolder.objects.filter(user_id=user_id)

        # 폴더에 속하는 북마크들을 조회
        bookmarks = Bookmark.objects.filter(favorite=True,
                                            deleted_at__isnull=True,
                                            folder_id__in=folders.values_list('id', flat=True))

        bookmarks_data = [BookmarkSerializer(bookmark).data for bookmark in bookmarks]

        # Serializer 인스턴스 생성 시 data 인자를 전달
        serializer = BookmarkSerializer(data=bookmarks_data, many=True)

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Bookmark.DoesNotExist:
        return Response({'message': 'No such favorite bookmark'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method = "patch", response_body="toggle bookmark")
@api_view(['PATCH'])
def toggle_favorite_bookmark(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id)
    except:
        return Response( {'message': 'No such bookmark'}, status=status.HTTP_400_BAD_REQUEST)

    if bookmark.favorite:
        bookmark.favorite = False
        bookmark.save()
        return Response({'favorite': bookmark.favorite},status=status.HTTP_200_OK)

    else:
        bookmark.favorite = True
        bookmark.save()
        return Response({'favorite': bookmark.favorite},status=status.HTTP_200_OK)



# @api_view(['GET'])
# def alarm_list(request, user_id):
#   deleted_bookmarks = Bookmark.objects.exclude(deleted_at__isnull=False)
