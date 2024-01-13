from rest_framework import serializers
from accountinfo.models import accountinfo

class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['email', 'id', 'user_name']
class UserSigninSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['email', 'password']

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['email', 'password','user_name']
