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
@swagger_auto_schema(method='post', request_body=UserSerializer,
                     operation_summary="임시적인 회원 생성", tags=['회원관리'],)
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
@swagger_auto_schema(method = "post", request_body = FolderSerializer,
                     tags=['폴더 관련'],operation_summary="폴더 생성")
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
@swagger_auto_schema(method = "get", response_body = FolderSerializer,
                     tags=['폴더 관련'],operation_summary="유저의 폴더 조회")
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
@swagger_auto_schema(method = "get", response_body = BookmarkSerializer,
                     tags=['북마크 관련'],operation_summary="특정 폴더 내부의 북마크 조회")
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
@swagger_auto_schema(method='post',request_body=BookmarkSerializer,
                     tags=['북마크 관련'],operation_summary="북마크 생성")
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
@swagger_auto_schema(method='delete', response_body=BookmarkSerializer,
                     tags=['북마크 관련'],operation_summary="북마크 삭제")
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


# 북마크 폴더 이동 함수
@swagger_auto_schema(method='patch', request_body=move_BookmarkSerializer,
                     tags=['북마크 관련'],operation_summary='북마크 이동(다른 폴더로 옮기기)')
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
@swagger_auto_schema(method = "patch", request_body=update_delete_BookmarkSerializer,
                     tags=['북마크 관련'], operation_summary='북마크 수정(이름, url)')
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
            if Bookmark.objects.filter(folder_id=folder_id, url=new_url,
                                       deleted_at__isnull=True).exclude(id=bookmark.id).exists():
                return Response({'error': 'This URL is already associated with another bookmark in the same folder.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if Bookmark.objects.filter(folder_id=folder_id, name=new_name,
                                       deleted_at__isnull=True).exclude(id=bookmark.id).exists():
                return Response({'error': 'This name is already associated with another bookmark in the same folder.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # 유효성 검사를 통과하고 중복이 없으면 저장
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Bookmark.DoesNotExist:
        return Response({'error': 'Bookmark not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(method='PATCH', request_body=update_delete_FolderSerializer,
                     tags=['폴더 관련'], operation_summary='폴더 이름 수정')
@api_view(['PATCH'])
def update_folder(request, folder_id):
    try:
        folder = BookmarkFolder.objects.get(id=folder_id)
        new_name = request.data.get('name', folder.name)

        folder.name = new_name
        folder.updated_at = timezone.now()
        folder.save()

        return Response({'id' : folder.id,
                         'name': folder.name
                         }, status=status.HTTP_200_OK)

    except BookmarkFolder.DoesNotExist:
        return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(method='DELETE', response_body='Success',
                     tags=['폴더 관련'],operation_summary='폴더와 종속된 북마크 삭제')
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






@swagger_auto_schema(method = "get", response_body=favorite_BookmarkSerializer,
                     tags=['즐겨찾기 관련'], operation_summary='즐겨찾기 리스트 조회')
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


@swagger_auto_schema(method = "patch", response_body="toggle bookmark",
                     tags=['즐겨찾기 관련'],operation_summary='즐겨찾기 등록, 삭제(toggle)')
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







