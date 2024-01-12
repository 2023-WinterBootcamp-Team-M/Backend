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

@csrf_exempt
@require_http_methods(["POST"])
def summary(request):
    try:
        openai.api_key = env('OPENAI_API_KEY')
        data = json.loads(request.body)

        # Extracting URL and summary length from the request
        url = data.get('url')
        summary_length = data.get('summary_length', 6)  # Default to 6-line summary

        content = crawl_url(url)

        # Adjust the request to OpenAI based on summary_length
        summary_request = "Please summarize the entire text content in "
        if summary_length == 3:
            summary_request += "three lines."
        else:
            summary_request += "six lines."
        summary_request += " Please answer in Korean."

        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": summary_request
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