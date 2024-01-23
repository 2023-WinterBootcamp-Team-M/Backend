from django.http import HttpResponse
from django_back.celery import app as celery_app
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from accountinfo.models import accountoptions, accountinfo
from bookmark.serializer import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from .tasks import *
from bookmark.utils import summary_three, summary_six, call_chatgpt_api, new_bookmark
import environ


env = environ.Env()
env.read_env()
# 폴더 생성 API
# 수정 필요

@swagger_auto_schema(method = "post", request_body = FolderCreateSerializer,
                     tags=['폴더 관련'],operation_summary="폴더 생성")
@api_view(['POST'])
def create_folder(request):
    user_id = request.user.id
    data = request.data
    serializer = FolderSerializer(data=data)

    # 폴더 이름 중복 처리
    if BookmarkFolder.objects.filter(name= data['name'], user_id=user_id, deleted_at__isnull=True).exists():
        return Response('The folder already exists', status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    return Response(serializer.errors,
        status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='PATCH', request_body=update_delete_FolderSerializer,
                     tags=['폴더 관련'], operation_summary='폴더 이름 수정')
@swagger_auto_schema(method='DELETE', response_body='Success',
                     tags=['폴더 관련'], operation_summary='폴더와 종속된 북마크 삭제')
@api_view(['PATCH', 'DELETE'])
def update_delete_folder(request, folder_id):
    if request.method == 'PATCH':
        try:
            data = request.data
            user_id = data.get('user_id')
            folder = BookmarkFolder.objects.get(id=folder_id)

            if BookmarkFolder.objects.filter(name=data['name'], user_id=user_id, deleted_at__isnull=True).exists():
                return Response('The folder already exists', status=status.HTTP_400_BAD_REQUEST)

            new_name = request.data.get('name', folder.name)
            folder.name = new_name
            folder.updated_at = timezone.now()
            folder.save()

            return Response({'id': folder.id,
                             'name': folder.name
                             }, status=status.HTTP_200_OK)

        except BookmarkFolder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)


    elif request.method == 'DELETE':
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

@swagger_auto_schema(method="get", response_body = BookmarkSerializer,
                     tags=['북마크 관련'],operation_summary="북마크의 요약 정보 조회")
@api_view(['GET'])
def get_bookmarks_summary(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id)
        folder = BookmarkFolder.objects.get(id=bookmark.folder_id.id, deleted_at__isnull=True)

        option = accountoptions.objects.get(accountid=folder.user_id.id, deleted_at__isnull=True)

        if option.summarizeoption:
            summary = bookmark.long_summary
        else:
            summary = bookmark.short_summary

        return Response({'summary': summary}, status=status.HTTP_200_OK)

    except Bookmark.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method="post",request_body=BookmarkclassifySerializer,
                     tags=['북마크 관련'], operation_summary='북마크 생성 및 폴더 분류')
@api_view(['POST'])
def create_classify_bookmark(request, user_id):
    data = request.data
    bookmark_name = data.get("name")
    bookmark_url = data.get("url")
    # 북마크 URL 분석을 통해 카테고리 결정
    category = call_chatgpt_api(bookmark_url,user_id)

    # 카테고리명을 키로 하여 북마크 정보를 JSON 형식으로 구성
    # response_data = {
    #     category: [
    #         {
    #             "name": bookmark_name,
    #             "url": bookmark_url
    #         }
    #     ]
    # }

    user_instance = accountinfo.objects.get(id=user_id)
    # 같은 폴더 있으면
    if BookmarkFolder.objects.filter(name=category,user_id=user_instance).exists():
        folder = BookmarkFolder.objects.get(name=category)
        bookmark = new_bookmark(bookmark_name,bookmark_url,folder.id)
    else:
        folder = BookmarkFolder(name=category, user_id=user_instance)
        folder.save()
        bookmark = new_bookmark(bookmark_name,bookmark_url, folder.id)

    folder_serializer = FolderSerializer(folder)
    bookmark_serializer = BookmarkSerializer(bookmark)

    #직렬화된 데이터를 응답으로 사용
    response_data = {
        'folder': folder_serializer.data,
        'bookmark': bookmark_serializer.data,
    }

    return Response(response_data, status=status.HTTP_200_OK)



# 북마크 생성 API
# 크롬북마크 API -> DRF -> Open ai API -> 북마크 분류 API
# api 가 던져준 북마크 name에 넣어져야 함
@swagger_auto_schema(method='post',request_body=BookmarkCreateSerializer,
                     tags=['북마크 관련'],operation_summary="북마크 생성")
@api_view(['POST'])
def create_bookmark(request):
    data = request.data
    # url하고 이름은 클라이언트가 지정하는 걸로 결정
    url = data.get('url')
    name = data.get('name')
    folder_id = data.get('folder_id')

    try:
        folder = BookmarkFolder.objects.get(id=folder_id)
    except BookmarkFolder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    if Bookmark.objects.filter(folder_id__user_id=folder.user_id, url=url,
                                              deleted_at__isnull=True).exists():
        return Response({'error': 'Bookmark with the same URL already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    if Bookmark.objects.filter(folder_id__user_id=folder.user_id, name=name,
                                              deleted_at__isnull=True).exists():
        return Response({'error': 'Bookmark with the same name already exists.'}, status=status.HTTP_400_BAD_REQUEST)


    short_summary = summary_three(url)
    long_summary = summary_six(url)


    serializer = BookmarkSerializer(data=data)
    # 직렬화할 데이터에 short_summary와 long_summary 추가


    if serializer.is_valid():
        serializer.validated_data['short_summary'] = short_summary
        serializer.validated_data['long_summary'] = long_summary

        # if url.endswith('.com/'):
        #     serializer.validated_data['icon'] = url + 'favicon.ico'

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 북마크 삭제 API
# 일단 우리가 아는 삭제가 아님 -> 기술적 삭제임 즉 deleted_at이 NULL이 아님.
# 삭제했던 것을 다시 부활시키면 Null로 해줘

@swagger_auto_schema(method = "patch", request_body=update_delete_BookmarkSerializer,
                     tags=['북마크 관련'], operation_summary='북마크 수정(이름, url)')
@swagger_auto_schema(method='delete', response_body=BookmarkSerializer,
                     tags=['북마크 관련'],operation_summary="북마크 삭제")
@api_view(['PATCH','DELETE'])
def update_delete_bookmark(request, folder_id, bookmark_id):
    if request.method == 'PATCH':
        try:
            data = request.data
            folder = BookmarkFolder.objects.get(id=folder_id)
            user_id = folder.user_id
            # 기존 북마크 가져오기
            bookmark = Bookmark.objects.get(id=bookmark_id)

            # Serializer를 사용하여 데이터 유효성 검사 및 업데이트
            serializer = BookmarkSerializer(bookmark, data=data, partial=True)

            if serializer.is_valid():
                new_url = serializer.validated_data.get('url', bookmark.url)
                new_name = serializer.validated_data.get('name', bookmark.name)

                # 기존과 동일한 'url' 또는 'name'을 가진 다른 북마크가 있는지 확인
                if Bookmark.objects.filter(folder_id=folder_id, url=new_url,
                                           deleted_at__isnull=True).exclude(id=bookmark.id).exists():
                    return Response(
                        {'error': 'This URL is already associated with another bookmark in the same folder.'},
                        status=status.HTTP_400_BAD_REQUEST)

                if Bookmark.objects.filter(folder_id=folder_id, name=new_name,
                                           deleted_at__isnull=True).exclude(id=bookmark.id).exists():
                    return Response(
                        {'error': 'This name is already associated with another bookmark in the same folder.'},
                        status=status.HTTP_400_BAD_REQUEST)

                if 'url' in request.data:
                    serializer.validated_data['short_summary'] = summary_three(new_url)
                    serializer.validated_data['long_summary'] = summary_six(new_url)

                serializer.validated_data['updated_at'] = timezone.now()
                # 유효성 검사를 통과하고 중복이 없으면 저장
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Bookmark.DoesNotExist:
            return Response({'error': 'Bookmark not found'}, status=status.HTTP_404_NOT_FOUND)


    elif request.method == 'DELETE':
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

@swagger_auto_schema(method='get', tags=['알림 관련'],operation_summary='알림 유무 조회')
@swagger_auto_schema(method='delete',tags=['알림 관련'],operation_summary='알림 확인')
@api_view(['GET','DELETE'])
def get_check_reminders(request,user_id):
    if request.method == 'GET':
        if Reminder.objects.filter(user_id=user_id, is_checked=False).exists():
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


    elif request.method == 'DELETE':
        reminders = Reminder.objects.filter(user_id=user_id)
        reminders.update(is_checked=True)  # Use update to efficiently update multiple records
        serializers = ReminderSerializer(reminders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

@swagger_auto_schema(method='get',tags=['알림 관련'],operation_summary='알림 목록 조회')
@api_view(['GET'])
def reminders_list(request, user_id):
    reminders = Reminder.objects.filter(user_id=user_id)
    reminders_data = [ReminderSerializer(reminder).data for reminder in reminders]

    # Serializer 인스턴스 생성 시 data 인자를 전달
    serializer = ReminderSerializer(data=reminders_data, many=True)

    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(method='delete',tags=['알림 관련'],operation_summary='해당 알림 삭제')
@api_view(['DELETE'])
def delete_reminders(request,reminder_id):
    reminder = Reminder.objects.get(id=reminder_id)
    reminder.delete()
    return Response({'message': 'delete'}, status=status.HTTP_200_OK)

def start_celery_task(request):
    # 작업 파라미터가 필요 없다면 별도의 파라미터 추출 부분은 생략할 수 있습니다.
    # Celery 작업 실행
    result = want_result.delay()
    # 작업 ID를 클라이언트에 반환
    return HttpResponse({'task_id': result.id})


def call_method(request):
    r = celery_app.send_task('tasks.want_result')
    #kwargs = {'x': random.randrange(0, 10), 'y': random.randrange(0, 10)
    return HttpResponse(r.id)


def get_status(request, task_id):
    status = celery_app.AsyncResult(task_id, app=celery_app)
    return HttpResponse("Status " + str(status.state))


def task_result(request, task_id):
    result = celery_app.AsyncResult(task_id).result
    return HttpResponse("Result " + str(result))




