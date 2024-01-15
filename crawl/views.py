import json
from django.http import JsonResponse

from .utils import crawl_url
import openai
import environ

env = environ.Env()
env.read_env()


def summary_three(request):
    try:
        openai.api_key = env('OPENAI_API_KEY')
        data = json.loads(request.body)
        url = data.get('url')

        content = crawl_url(url)

        # Adjust the request to OpenAI based on summary_length
        summary_request = ("Please summarize the entire text content in three lines.\
                           Please answer in Korean.")

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


def summary_six(request):
    try:
        openai.api_key = env('OPENAI_API_KEY')
        data = json.loads(request.body)

        url = data.get('url')

        content = crawl_url(url)

        # Adjust the request to OpenAI based on summary_length
        summary_request = ("Please summarize the entire text content in six lines.\
                            Please answer in Korean.")

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