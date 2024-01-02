# Base 이미지 설정
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update

# 소스 코드 복사
COPY . ./django_back