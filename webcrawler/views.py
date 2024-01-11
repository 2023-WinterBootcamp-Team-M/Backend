import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from .utils import crawl_url
from bs4 import BeautifulSoup
import openai
import environ

env = environ.Env()
env.read_env()

@csrf_exempt  # CSRF 토큰을 무시하도록 설정
@require_http_methods(["POST"])
def summary(request):
    try:
        openai.api_key = env('OPENAI_API_KEY')
        data = json.loads(request.body)
        url = data.get('url')
        content = crawl_url(url)

        response = openai.chat.completions.create(
            model="gpt-4",  # 적합한 모델 선택
            messages=[
                {
                    "role": "system",
                    "content": "Please summarize the entire text content in three lines. Please answer in Korean."
                },
                {
                    "role": "user",
                    "content": content
                },
            ],
        )
        return JsonResponse({'summary': response.choices[0].message.content}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)