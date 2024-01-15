import re
import json
from urllib import request
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accountinfo.serializers import UserSignupSerializer, UserSigninSerializer, UserProfileSerializer, UserDeleteSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from accountinfo.models import accountinfo
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.utils import timezone  # timezone 모듈 임포트 추가

# Create your views here.
@swagger_auto_schema(method='delete', response_body='delete')
@api_view(['DELETE'])
def delete_user(request, user_id):
    # 세션에서 사용자 아이디 가져오기
    #email = request.session.get('email')
    account = accountinfo.objects.get(id= user_id)

    if account.deleted_at is None:
        # 사용자 모델에서 사용자 객체 가져오기
        #user = get_object_or_404(accountinfo, account)

        # 사용자의 날짜 필드 업데이트
        account.deleted_at = timezone.now()
        account.save()

        return Response({"deleted_at": account.deleted_at}, status=status.HTTP_200_OK)
    else:
        return Response({'messege': '이미 삭제되었습니다.'},status=status.HTTP_400_BAD_REQUEST)

# @swagger_auto_schema(method='GET', response_body='get ok')
# @api_view(['GET'])
# def profile_get(user_id):
#     profile = accountinfo.objects.get(email=email)
#     return Response(profile.data, status=status.HTTP_200_OK)

@swagger_auto_schema(method='put', request_body=UserSignupSerializer)
@api_view(['PUT'])
def profile_edit(request):
    info = accountinfo.objects.get(email=request.data['email'])

    # 변경하고자 하는 필드를 클라이언트에서 받아옴
    new_email = request.data.get('email', info.email).strip()
    new_password = request.data.get('password', info.password).strip()
    new_user_name = request.data.get('user_name', info.user_name).strip()

    # 서버 측에서는 변경하고자 하는 필드만 업데이트
    if new_email:
        info.email = new_email
    if new_password:
        info.password = new_password
    if new_user_name:
        info.user_name = new_user_name

    info.updated_at = timezone.now()

    # 저장
    info.save()
    return Response({
            "email" : info.email,
            "password" : info.password,
            "user_name" : info.user_name},
            status=status.HTTP_200_OK)


    # elif request.method == 'GET':
    #     email = request.session.get('email', None)
    #     profile = accountinfo.objects.get(email=email)
    #     return Response(profile.data, status=status.HTTP_200_OK)

    # 업데이트된 게시글을 JSON 응답으로 반환
    # serializer = UserSignupSerializer(data = info)
    # if serializer.is_valid():
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    # else:
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# return Response(info, status.HTTP_202_ACCEPTED)


def logout(request, email):
    if email in request.session:
        del request.session[email]
        return Response({
            "message": "로그아웃 완료"
        }, status=200)
    else:
        return Response({
            "message": "요청하신 정보가 올바르지 않습니다."
        },status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body=UserSigninSerializer)
@api_view(['POST'])
def signin(request):
    # signininfo = UserSigninSerializer(data=request.data)
    #
    # email = signininfo.validated_data.get('email')
    # password = signininfo.validated_data.get('password')
    email = request.data.get('email')
    password = request.data.get('password')

    if accountinfo.objects.filter(email=email, password=password).exists():
        # request.session['email'] = (email)
        user = accountinfo.objects.get(email=email)
        #userinfo = UserProfileSerializer(data=user)
        return Response({
            "email": user.email,
            "id": user.id,
            "name": user.user_name,
        },status=status.HTTP_200_OK)
        # if userinfo.is_valid():
        #     return Response(userinfo.data, status=status.HTTP_200_OK)
        # else:
        #     return Response(userinfo.errors, status=status.HTTP_401_UNAUTHORIZED)
    else:
     return Response({
         'message' : '입력 정보 확인 부탁드립니다.'
     },status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return Response({
    #              'message22222222222' : signininfo.errors
    #          },status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body=UserSignupSerializer)
@api_view(['POST'])
def signup(request):
    signupinfo = UserSignupSerializer(data=request.data)
    if signupinfo.is_valid():
        signupinfo.save()

        return Response({
            'message': '회원가입 완료',
        }, status=status.HTTP_200_OK)

    return Response({
        'message': '입력정보를 확인하여 주십시오',
    }, status=status.HTTP_400_BAD_REQUEST)