# evercoin/backend/api/users/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email as django_validate_email
from django.conf import settings

def validate_password_strength(password):
    """
    Валидатор силы пароля.
    Проверяет, что пароль соответствует требованиям безопасности:
    - Минимум 8 символов
    - Хотя бы одна заглавная буква
    - Хотя бы одна цифра  
    - Хотя бы один специальный символ
    - Проверка на распространенные пароли
    """
    if len(password) < 8:
        raise ValidationError(
            "Пароль должен содержать минимум 8 символов.",
            code='password_too_short'
        )
    
    # Проверка нескольких категорий символов для большей безопасности
    categories = 0
    if re.search(r'[A-ZА-Я]', password): categories += 1
    if re.search(r'[a-zа-я]', password): categories += 1  
    if re.search(r'[0-9]', password): categories += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>\[\]\\/+_\-=]', password): categories += 1
    
    if categories < 3:
        raise ValidationError(
            "Пароль должен содержать символы из至少 3 категорий: заглавные буквы, строчные буквы, цифры, специальные символы.",
            code='password_too_simple'
        )
    
    # Проверка на распространенные пароли
    common_passwords = [
        'password', '12345678', 'qwertyui', 'admin123', 'welcome',
        'пароль', '123456789', '11111111', '00000000'
    ]
    
    if password.lower() in common_passwords:
        raise ValidationError(
            "Этот пароль слишком распространен и ненадежен.",
            code='password_common'
        )


def validate_email_format(email):
    """
    Валидатор формата email.
    Проверяет корректность формата email с помощью стандартного валидатора Django.
    """
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError(
            "Введите корректный email адрес.",
            code='invalid_email'
        )
    
    # Дополнительная проверка домена
    if hasattr(settings, 'RESTRICTED_EMAIL_DOMAINS'):
        restricted_domains = getattr(settings, 'RESTRICTED_EMAIL_DOMAINS', [])
        domain = email.split('@')[-1]
        if domain in restricted_domains:
            raise ValidationError(
                "Регистрация с данного домена невозможна.",
                code='restricted_domain'
            )
