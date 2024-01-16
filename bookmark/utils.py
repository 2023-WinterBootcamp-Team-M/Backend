import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from bs4 import BeautifulSoup

import openai
import environ
from rest_framework.response import Response
env = environ.Env()
env.read_env()

def crawl_url(url):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ko-KR,kr;q=0.9, en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,la;q=0.6',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()



def summary_three(url):
    try:
        openai.api_key = env('OPENAI_API_KEY')
        # data = json.loads(request.body)
        # url = data.get('url')

        content = crawl_url(url)

        # Adjust the request to OpenAI based on summary_length
        summary_request = ("Please summarize the entire text content in 140 characters.\
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
        summary_content = response.choices[0].message.content
        return summary_content
    except Exception as e:
        return {'error': str(e)}


def summary_six(url):
    try:
        openai.api_key = env('OPENAI_API_KEY')
        # data = json.loads(request.body)
        #
        # url = data.get('url')

        content = crawl_url(url)

        # Adjust the request to OpenAI based on summary_length
        summary_request = ("Please summarize the entire text content in 280 characters.\
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
        summary_content = response.choices[0].message.content
        return summary_content
    except Exception as e:
        return {'error': str(e)}