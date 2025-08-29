# evercoin/backend/api/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from .validators import validate_email_format

class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая стандартную AbstractUser.
    Использует email в качестве основного идентификатора вместо username.
    """
    
    username = models.CharField(
        'имя пользователя',
        max_length=150,
        unique=True,
        help_text='Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    
    email = models.EmailField(
        'email адрес',
        unique=True,
        validators=[validate_email_format],
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        },
    )
    
    profile_image = models.ImageField(
        'аватарка',
        upload_to='profile_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    
    # Указываем, что email используется для аутентификации вместо username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """
        Удаление старого изображение при обновлении
        """
        if self.pk:
            try:
                old_instance = CustomUser.objects.get(pk=self.pk)
                if old_instance.profile_image and old_instance.profile_image != self.profile_image:
                    old_instance.profile_image.delete(save=False)
            except CustomUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """
    Модель для хранения токенов сброса пароля.
    Каждый токен связан с пользователем и имеет ограниченное время жизни.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='password_reset_tokens'
        )
    token = models.CharField('токен', max_length=100, unique=True)
    created_at = models.DateTimeField('создан', auto_now_add=True)
    expires_at = models.DateTimeField('истекает')
    is_used = models.BooleanField('использован', default=False)

    def is_valid(self):
        """
        Проверяет, действителен ли токен.
        Возвращает True если токен не использован и не истек срок действия.
        """
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at

    class Meta:
        verbose_name = 'токен сброса пароля'
        verbose_name_plural = 'токены сброса пароля'
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['user', 'is_used']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Токен для {self.user.email} (истекает: {self.expires_at})"
