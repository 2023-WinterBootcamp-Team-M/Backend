from django.shortcuts import render
import json
import re
import openai
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import environ

from bookmark.models import BookmarkFolder, Bookmark, User
from bookmark.serializer import BookmarkSerializer, FolderSerializer

# Create your views here.

env = environ.Env()
env.read_env()

def call_chatgpt_api(bookmark_url,user_id):
    openai.api_key = env('OPENAI_API_KEY')

    categorize_request = ("Please categorize the contents of these links into about 10 categories and organize the links into each folder accordingly.\
                          The language of the folder name is Korean.\
                          If one bookmark is added, please include this data in the categories we identified earlier.\
                          Please provide the output in JSON format.\
                          Please answer in Korean.\ ")

    # folders = folder_data_list(user_id)
    # content = bookmark_url + ' '.join(folders) if folders else bookmark_url
    Flist = folder_data_list(user_id)

    # 폴더 이름과 해당 폴더에 속한 북마크 URL을 추출하여 content에 추가
    content = bookmark_url
    for folder_data in Flist:
        folder_name = folder_data['folder_name']
        bookmarks = folder_data['bookmarks']

        # 폴더 이름과 북마크 정보를 content에 추가
        content += f"\n폴더 이름: {folder_name}\n북마크 목록:\n"
        for bookmark in bookmarks:
            bookmark_name = bookmark['name']
            bookmark_url = bookmark['url']
            content += f"  - 북마크 이름: {bookmark_name}, 북마크 URL: {bookmark_url}\n"

    # 만약 폴더가 하나도 없다면, 기본 URL만 남깁니다.
    content = content if folder_data_list else bookmark_url

    # 만약 폴더가 하나도 없다면, 기본 URL만 남깁니다.
    content = content if folder_data_list else bookmark_url

    response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": categorize_request
            },
            {
                "role": "user",
                "content": content
            }
        ],
    )

    latest_response = response.choices[0].message.content.strip()

    # JSON 형식의 문자열 추출
    json_str_match = re.search(r"```json\n(.*)\n```", latest_response, re.DOTALL)
    if json_str_match:
        json_str = json_str_match.group(1).strip()

        # JSON 문자열 파싱
        try:
            json_data = json.loads(json_str)
            category = list(json_data.keys())[0]
            return category
        except json.JSONDecodeError:
            pass

    # 기본 카테고리 반환 (분석 실패 시)
    return "기타"



def create_bookmark(bookmark_name,bookmark_url, folder_id):
    folder_instance = BookmarkFolder.objects.get(id=folder_id)
    bookmark = Bookmark(name=bookmark_name,
                                       url=bookmark_url, folder_id=folder_instance)
    bookmark.clean()
    bookmark.save()
    return bookmark

# def folder_name_list(user_id):
#     try:
#         user_id = User.objects.get(id=user_id)
#         folders = BookmarkFolder.objects.filter(user_id=user_id, deleted_at__isnull=True)
#         serializer = FolderSerializer(folders, many=True)
#
#         folder_names = [item['name'] for item in serializer.data]
#         return folder_names
#
#     except BookmarkFolder.DoesNotExist:
#         return None
def folder_data_list(user_id):
    try:
        user = User.objects.get(id=user_id)
        folders = BookmarkFolder.objects.filter(user_id=user, deleted_at__isnull=True)
        folder_data_list = []

        for folder in folders:
            folder_data = {
                'folder_name': folder.name,
                'bookmarks': [{'name': bookmark.name, 'url': bookmark.url} for bookmark in folder.bookmark_set.all()]
            }
            folder_data_list.append(folder_data)

        return folder_data_list

    except User.DoesNotExist:
        return None

# Based on the URL and name, create folder names that fit the category and output this in JSON format.\
#                           Only include the input values we provided, without any examples.\
#                           Rather than focusing on a single element like 'Developer Community' or 'Cloud Service Management', group such elements under broader categories like 'Development'. \
#                           Create folders from this wider perspective.\
#                           The language of the folder name is Korean.\
#                           If one bookmark is added, please include this data in the categories we identified earlier.\
#                           Please provide the output in JSON format.\
#                           Please answer in Korean.\

# Based on the URL and name, create folder names that fit the category and output this in JSON format. \
#     Only include the input values we provided, without any examples.\
#     The language of the folder name is Korean.\
#     If one bookmark is added, please include this data in the categories we identified earlier.\
#     Please provide the output in JSON format.\
#     lease answer in Korean.\
