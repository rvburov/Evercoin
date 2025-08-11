import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.yandex.provider import YandexProvider
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import CustomUserSerializer, SocialLoginSerializer

class AccountView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class AccountUpdateView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class AccountDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

class YandexOAuth2Adapter(OAuth2Adapter):
    provider_id = YandexProvider.id
    access_token_url = 'https://oauth.yandex.ru/token'
    authorize_url = 'https://oauth.yandex.ru/authorize'
    profile_url = 'https://login.yandex.ru/info'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={'format': 'json', 'oauth_token': token.token}
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)

class YandexLogin(SocialLoginView):
    adapter_class = YandexOAuth2Adapter
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
