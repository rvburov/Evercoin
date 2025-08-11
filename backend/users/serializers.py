from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import CustomUser

class CustomUserSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        model = CustomUser
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)

class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }

    def save(self, request):
        cleaned_data = self.get_cleaned_data()
        user = CustomUser.objects.create_user(
            email=cleaned_data['email'],
            password=cleaned_data['password1']
        )
        return user

class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    id_token = serializers.CharField(required=False)
