from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer
from .models import CustomUser

class CustomUserSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        model = CustomUser
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)

class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
