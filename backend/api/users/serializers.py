# evercoin/backend/api/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .validators import validate_password_strength, validate_email_format

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Включает подтверждение пароля и валидацию данных.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password_strength],
        style={'input_type': 'password'},
        label='пароль'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='подтверждение пароля'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'validators': [validate_email_format]},
            'username': {'label': 'имя пользователя'},
            'email': {'label': 'email адрес'},
        }

    def validate(self, attrs):
        """
        Проверяет, что пароль и подтверждение пароля совпадают.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        """
        Создает нового пользователя с валидированными данными.
        Удаляет поле подтверждения пароля перед созданием.
        """
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    Проверяет email и пароль, аутентифицирует пользователя.
    """
    
    email = serializers.EmailField(required=True, label='email адрес')
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        label='пароль'
    )

    def validate(self, attrs):
        """
        Аутентифицирует пользователя по email и паролю.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            
            if not user:
                msg = 'Неверные учетные данные для входа.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Необходимо указать "email" и "пароль".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения и обновления данных пользователя.
    Исключает чувствительные данные like пароль.
    """
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'profile_image')
        read_only_fields = ('id', 'email')  # Email нельзя менять после регистрации
        extra_kwargs = {
            'username': {'label': 'имя пользователя'},
            'email': {'label': 'email адрес'},
            'profile_image': {'label': 'аватарка'},
        }
    
    def validate_profile_image(self, value):
        """
        Валидация изображения профиля
        """
        if value:
            # Проверка размера файла (максимум 5MB)
            if hasattr(value, 'size') and value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Размер файла слишком большой (максимум 5MB)")
            
            # Проверка типа файла
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError("Неподдерживаемый тип файла")
        
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля.
    Проверяет старый пароль и валидирует новый.
    """
    
    old_password = serializers.CharField(required=True, label='старый пароль')
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password_strength],
        label='новый пароль'
    )


class PasswordResetSerializer(serializers.Serializer):
    """
    Сериализатор для запроса сброса пароля.
    Принимает email пользователя.
    """
    
    email = serializers.EmailField(required=True, label='email адрес')


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля.
    Принимает токен и новый пароль.
    """
    
    token = serializers.CharField(required=True, label='токен')
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password_strength],
        label='новый пароль'
    )
