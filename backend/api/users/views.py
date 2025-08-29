# evercoin/backend/api/users/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import secrets
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
import logging

from .models import CustomUser, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)

logger = logging.getLogger(__name__)

class UserRegistrationView(generics.CreateAPIView):
    """
    Представление для регистрации нового пользователя.
    Разрешает доступ без аутентификации.
    """
    
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Создает нового пользователя и возвращает JWT токены.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Генерация JWT токенов
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")
        
        return Response({
            "message": "Пользователь успешно создан",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    Представление для входа пользователя с JWT аутентификацией.
    """
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """
        Обрабатывает POST запрос для входа пользователя.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Генерация JWT токенов
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"User logged in: {user.email}")
        
        return Response({
            "message": "Вход выполнен успешно",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })


class UserLogoutView(generics.GenericAPIView):
    """
    Представление для выхода пользователя.
    Добавляет refresh token в blacklist.
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return None 

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {"error": "Требуется refresh токен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out: {request.user.email}")
            return Response({"message": "Выход выполнен успешно"})
            
        except Exception as e:
            return Response(
                {"error": "Неверный токен"},
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountDetailView(generics.RetrieveAPIView):
    """
    Представление для получения детальной информации о текущем пользователе.
    Требует аутентификации.
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AccountUpdateView(generics.UpdateAPIView):
    """
    Представление для обновления данных текущего пользователя.
    Требует аутентификации.
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        """
        Возвращает текущего аутентифицированного пользователя для обновления.
        """
        return self.request.user

    def perform_update(self, serializer):
        """
        Логирование обновления профиля.
        """
        instance = serializer.save()
        logger.info(f"User profile updated: {instance.email}")


class AccountDeleteView(generics.DestroyAPIView):
    """
    Представление для удаления аккаунта текущего пользователя.
    Требует аутентификации.
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Возвращает текущего аутентифицированного пользователя для удаления.
        """
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет аккаунт текущего пользователя.
        """
        user = self.get_object()
        user_email = user.email
        user.delete()
        
        logger.warning(f"User account deleted: {user_email}")
        
        return Response({"message": "Аккаунт успешно удален"})


class PasswordChangeView(generics.GenericAPIView):
    """
    Представление для смены пароля текущего пользователя.
    Требует аутентификации и проверки старого пароля.
    """
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        """
        Обрабатывает запрос на смену пароля.
        Проверяет старый пароль и устанавливает новый.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"error": "Текущий пароль указан неверно"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        logger.info(f"Password changed for user: {user.email}")
        
        return Response({"message": "Пароль успешно изменен"})


class PasswordResetView(generics.GenericAPIView):
    """
    Представление для запроса сброса пароля.
    Отправляет email с токеном для сброса пароля.
    """
    
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """
        Обрабатывает запрос на сброс пароля.
        Создает токен и отправляет email с ссылкой для сброса.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Всегда возвращаем одинаковый ответ для безопасности
        try:
            user = CustomUser.objects.get(email=email)
            
            # Удаляем старые токены пользователя
            PasswordResetToken.objects.filter(user=user, is_used=False).delete()
            
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=1)
            
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            reset_url = f"{settings.FRONTEND_URL}/password-reset/confirm/?token={token}"
            
            # Отправка email (в продакшне лучше использовать Celery)
            send_mail(
                subject="Сброс пароля",
                message=f"Для сброса пароля перейдите по ссылке: {reset_url}\n\nСсылка действительна 1 час.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            logger.info(f"Password reset email sent to: {email}")
            
        except CustomUser.DoesNotExist:
            # Логируем попытку сброса для несуществующего email
            logger.warning(f"Password reset attempt for non-existent email: {email}")
        
        return Response({"message": "Если email существует, ссылка для сброса отправлена"})


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Представление для подтверждения сброса пароля.
    Проверяет токен и устанавливает новый пароль.
    """
    
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """
        Обрабатывает подтверждение сброса пароля.
        Проверяет токен и обновляет пароль пользователя.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Неверный или просроченный токен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reset_token.is_valid():
            return Response(
                {"error": "Срок действия токена истек"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        reset_token.is_used = True
        reset_token.save()
        
        # Удаляем все неиспользованные токены пользователя
        PasswordResetToken.objects.filter(user=user, is_used=False).delete()
        
        logger.info(f"Пароль успешно сброшен для пользователя: {user.email}")
        
        return Response({"message": "Пароль успешно сброшен"})
