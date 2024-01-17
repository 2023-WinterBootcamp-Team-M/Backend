from rest_framework import serializers
from accountinfo.models import accountinfo, accountoptions


class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = '__all__'
        #fields = ['email', 'id', 'user_name']
class UserSigninSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['email', 'password']

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountinfo
        fields = ['email', 'password','user_name']

class OptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountoptions
        #fields = '__all__'
        fields = ['accountid', 'summarizeoption', 'startupoption', 'themeoption', 'bookmarkalertoption']

class OptionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountoptions
        fields = ['summarizeoption', 'startupoption', 'themeoption', 'bookmarkalertoption', 'updated_at']

class OptionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountoptions
        fields = ['summarizeoption', 'startupoption', 'themeoption', 'bookmarkalertoption']

class OptionIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = accountoptions
        fields = ['accountid']