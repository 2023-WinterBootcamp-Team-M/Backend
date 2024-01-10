import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from bs4 import BeautifulSoup
@csrf_exempt  # CSRF 토큰을 무시하도록 설정
@require_http_methods(["POST"])
def crawl_website(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        content = crawl_url(url)
        return JsonResponse({'content': content}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def crawl_url(url):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,la;q=0.6',
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
