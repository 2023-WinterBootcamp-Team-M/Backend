from django.shortcuts import render
import json
import re
import openai
from django.http import JsonResponse
from rest_framework.decorators import api_view

import environ
# Create your views here.

env = environ.Env()
env.read_env()
def call_chatgpt_api(bookmark_url):
    openai.api_key = env('OPENAI_API_KEY')

    categorize_request = "Please categorize the contents of these links into about 10 categories and organize the links into each folder accordingly. \
    The language of the folder name is Korean.\
    If one bookmark is added, please include this data in the categories we identified earlier.\
    Please provide the output in JSON format.\
    Please answer in Korean."
    content = bookmark_url

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


@api_view(['POST'])
def classify_bookmark(request):
    bookmark_data = request.data
    bookmark_name = bookmark_data.get("name")
    bookmark_url = bookmark_data.get("url")

    # 북마크 URL 분석을 통해 카테고리 결정
    category = call_chatgpt_api(bookmark_url)

    # 카테고리명을 키로 하여 북마크 정보를 JSON 형식으로 구성
    response_data = {
        category: [
            {
                "name": bookmark_name,
                "url": bookmark_url
            }
        ]
    }

    return JsonResponse(response_data)