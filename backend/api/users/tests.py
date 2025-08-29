# evercoin/backend/api/users/tests.py
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from PIL import Image
import io

from api.users.models import PasswordResetToken

User = get_user_model()

@pytest.fixture
def api_client():
    """Фикстура для API клиента"""
    return APIClient()

@pytest.fixture
def user_data():
    """Фикстура с данными пользователя для тестов"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'password_confirm': 'TestPassword123!'
    }

@pytest.fixture
def create_user():
    """Фикстура для создания пользователя"""
    def _create_user(email='test@example.com', username='testuser', password='TestPassword123!'):
        return User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
    return _create_user

@pytest.fixture
def authenticated_user(api_client, create_user):
    """Фикстура для аутентифицированного пользователя"""
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return user

@pytest.fixture
def temp_image():
    """Фикстура для создания временного изображения"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    image = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        "test_image.jpg",
        img_io.getvalue(),
        content_type="image/jpeg"
    )

@pytest.fixture
def email_backend_override():
    """Фикстура для переопределения email backend"""
    with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
        yield

@pytest.mark.django_db
class TestUserRegistrationView:
    """Тесты для представления регистрации пользователей"""

    def test_successful_registration(self, api_client, user_data):
        """Тест успешной регистрации"""
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
        assert User.objects.filter(email=user_data['email']).exists()

    def test_registration_duplicate_email(self, api_client, user_data, create_user):
        """Тест регистрации с уже существующим email"""
        create_user(email=user_data['email'])
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_duplicate_username(self, api_client, user_data, create_user):
        """Тест регистрации с уже существующим username"""
        create_user(username=user_data['username'])
        user_data['email'] = 'another@example.com'
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_password_mismatch(self, api_client, user_data):
        """Тест регистрации с несовпадающими паролями"""
        user_data['password_confirm'] = 'DifferentPassword123!'
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_registration_weak_password(self, api_client, user_data):
        """Тест регистрации со слабым паролем"""
        user_data['password'] = '123'
        user_data['password_confirm'] = '123'
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_missing_fields(self, api_client):
        """Тест регистрации с отсутствующими полями"""
        url = reverse('register')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_invalid_email(self, api_client, user_data):
        """Тест регистрации с некорректным email"""
        user_data['email'] = 'invalid-email'
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestUserLoginView:
    """Тесты для представления входа пользователей"""

    def test_successful_login(self, api_client, create_user):
        """Тест успешного входа"""
        user = create_user()
        
        url = reverse('login')
        login_data = {
            'email': user.email,
            'password': 'TestPassword123!'
        }
        response = api_client.post(url, login_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data

    def test_login_invalid_email(self, api_client):
        """Тест входа с несуществующим email"""
        url = reverse('login')
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPassword123!'
        }
        response = api_client.post(url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_wrong_password(self, api_client, create_user):
        """Тест входа с неверным паролем"""
        user = create_user()
        
        url = reverse('login')
        login_data = {
            'email': user.email,
            'password': 'WrongPassword123!'
        }
        response = api_client.post(url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_fields(self, api_client):
        """Тест входа с отсутствующими полями"""
        url = reverse('login')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_empty_email(self, api_client):
        """Тест входа с пустым email"""
        url = reverse('login')
        login_data = {
            'email': '',
            'password': 'TestPassword123!'
        }
        response = api_client.post(url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_empty_password(self, api_client, create_user):
        """Тест входа с пустым паролем"""
        user = create_user()
        
        url = reverse('login')
        login_data = {
            'email': user.email,
            'password': ''
        }
        response = api_client.post(url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestUserLogoutView:
    """Тесты для представления выхода пользователей"""

    def test_successful_logout(self, api_client, authenticated_user):
        """Тест успешного выхода"""
        refresh = RefreshToken.for_user(authenticated_user)
        
        url = reverse('logout')
        logout_data = {'refresh': str(refresh)}
        response = api_client.post(url, logout_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

    def test_logout_without_authentication(self, api_client):
        """Тест выхода без аутентификации"""
        url = reverse('logout')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_invalid_token(self, api_client, authenticated_user):
        """Тест выхода с невалидным токеном"""
        url = reverse('logout')
        logout_data = {'refresh': 'invalid-token'}
        response = api_client.post(url, logout_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_without_token(self, api_client, authenticated_user):
        """Тест выхода без токена"""
        url = reverse('logout')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestAccountDetailView:
    """Тесты для представления детальной информации об аккаунте"""

    def test_get_account_details(self, api_client, authenticated_user):
        """Тест получения информации об аккаунте"""
        url = reverse('account_detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == authenticated_user.email
        assert response.data['username'] == authenticated_user.username

    def test_get_account_details_without_authentication(self, api_client):
        """Тест получения информации без аутентификации"""
        url = reverse('account_detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestAccountUpdateView:
    """Тесты для представления обновления аккаунта"""

    def test_update_username(self, api_client, authenticated_user):
        """Тест обновления имени пользователя"""
        url = reverse('account_update')
        update_data = {'username': 'newusername'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        authenticated_user.refresh_from_db()
        assert authenticated_user.username == 'newusername'

    def test_update_profile_image(self, api_client, authenticated_user, temp_image):
        """Тест обновления изображения профиля"""
        url = reverse('account_update')
        
        update_data = {'profile_image': temp_image}
        response = api_client.patch(url, update_data, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
        authenticated_user.refresh_from_db()
        assert authenticated_user.profile_image is not None

    def test_update_readonly_field(self, api_client, authenticated_user):
        """Тест попытки обновления поля только для чтения (email)"""
        url = reverse('account_update')
        update_data = {'email': 'newemail@example.com'}
        response = api_client.patch(url, update_data, format='json')
        
        # Email не должен измениться
        authenticated_user.refresh_from_db()
        assert authenticated_user.email != 'newemail@example.com'

    def test_update_without_authentication(self, api_client):
        """Тест обновления без аутентификации"""
        url = reverse('account_update')
        update_data = {'username': 'newusername'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestAccountDeleteView:
    """Тесты для представления удаления аккаунта"""

    def test_delete_account(self, api_client, authenticated_user):
        """Тест удаления аккаунта"""
        user_id = authenticated_user.id
        
        url = reverse('account_delete')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not User.objects.filter(id=user_id).exists()

    def test_delete_account_without_authentication(self, api_client):
        """Тест удаления аккаунта без аутентификации"""
        url = reverse('account_delete')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestPasswordChangeView:
    """Тесты для представления смены пароля"""

    def test_successful_password_change(self, api_client, authenticated_user):
        """Тест успешной смены пароля"""
        url = reverse('password_change')
        change_data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewTestPassword123!'
        }
        response = api_client.post(url, change_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        authenticated_user.refresh_from_db()
        assert authenticated_user.check_password('NewTestPassword123!')

    def test_password_change_wrong_old_password(self, api_client, authenticated_user):
        """Тест смены пароля с неверным старым паролем"""
        url = reverse('password_change')
        change_data = {
            'old_password': 'WrongOldPassword!',
            'new_password': 'NewTestPassword123!'
        }
        response = api_client.post(url, change_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_change_weak_new_password(self, api_client, authenticated_user):
        """Тест смены пароля на слабый новый пароль"""
        url = reverse('password_change')
        change_data = {
            'old_password': 'TestPassword123!',
            'new_password': '123'
        }
        response = api_client.post(url, change_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_change_without_authentication(self, api_client):
        """Тест смены пароля без аутентификации"""
        url = reverse('password_change')
        change_data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewTestPassword123!'
        }
        response = api_client.post(url, change_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_password_change_missing_fields(self, api_client, authenticated_user):
        """Тест смены пароля с отсутствующими полями"""
        url = reverse('password_change')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestPasswordResetView:
    """Тесты для представления сброса пароля"""

    def test_successful_password_reset_request(self, api_client, create_user, email_backend_override):
        """Тест успешного запроса сброса пароля"""
        user = create_user()
        
        url = reverse('password_reset')
        reset_data = {'email': user.email}
        response = api_client.post(url, reset_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert PasswordResetToken.objects.filter(user=user).exists()

    def test_password_reset_nonexistent_email(self, api_client, email_backend_override):
        """Тест запроса сброса пароля для несуществующего email"""
        url = reverse('password_reset')
        reset_data = {'email': 'nonexistent@example.com'}
        response = api_client.post(url, reset_data, format='json')
        
        # Всегда возвращает success для безопасности
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_password_reset_invalid_email_format(self, api_client, email_backend_override):
        """Тест запроса сброса пароля с некорректным форматом email"""
        url = reverse('password_reset')
        reset_data = {'email': 'invalid-email'}
        response = api_client.post(url, reset_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_missing_email(self, api_client, email_backend_override):
        """Тест запроса сброса пароля без email"""
        url = reverse('password_reset')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_multiple_password_reset_requests(self, api_client, create_user, email_backend_override):
        """Тест множественных запросов сброса пароля"""
        user = create_user()
        
        url = reverse('password_reset')
        reset_data = {'email': user.email}
        
        # Первый запрос
        response1 = api_client.post(url, reset_data, format='json')
        assert response1.status_code == status.HTTP_200_OK
        
        # Второй запрос - старый токен должен быть удален
        response2 = api_client.post(url, reset_data, format='json')
        assert response2.status_code == status.HTTP_200_OK
        
        # Должен остаться только один активный токен
        active_tokens = PasswordResetToken.objects.filter(user=user, is_used=False)
        assert active_tokens.count() == 1

@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Тесты для представления подтверждения сброса пароля"""

    def test_successful_password_reset_confirm(self, api_client, create_user):
        """Тест успешного подтверждения сброса пароля"""
        user = create_user()
        
        # Создаем токен
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token='valid-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        url = reverse('password_reset_confirm')
        confirm_data = {
            'token': 'valid-token-123',
            'new_password': 'NewResetPassword123!'
        }
        response = api_client.post(url, confirm_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewResetPassword123!')
        
        reset_token.refresh_from_db()
        assert reset_token.is_used

    def test_password_reset_confirm_invalid_token(self, api_client):
        """Тест подтверждения сброса с недействительным токеном"""
        url = reverse('password_reset_confirm')
        confirm_data = {
            'token': 'invalid-token',
            'new_password': 'NewResetPassword123!'
        }
        response = api_client.post(url, confirm_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_expired_token(self, api_client, create_user):
        """Тест подтверждения сброса с истекшим токеном"""
        user = create_user()
        
        # Создаем истекший токен
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token='expired-token-123',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        url = reverse('password_reset_confirm')
        confirm_data = {
            'token': 'expired-token-123',
            'new_password': 'NewResetPassword123!'
        }
        response = api_client.post(url, confirm_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_used_token(self, api_client, create_user):
        """Тест подтверждения сброса с уже использованным токеном"""
        user = create_user()
        
        # Создаем использованный токен
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token='used-token-123',
            expires_at=timezone.now() + timedelta(hours=1),
            is_used=True
        )
        
        url = reverse('password_reset_confirm')
        confirm_data = {
            'token': 'used-token-123',
            'new_password': 'NewResetPassword123!'
        }
        response = api_client.post(url, confirm_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_weak_password(self, api_client, create_user):
        """Тест подтверждения сброса со слабым паролем"""
        user = create_user()
        
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token='valid-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        url = reverse('password_reset_confirm')
        confirm_data = {
            'token': 'valid-token-123',
            'new_password': '123'
        }
        response = api_client.post(url, confirm_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_missing_fields(self, api_client):
        """Тест подтверждения сброса с отсутствующими полями"""
        url = reverse('password_reset_confirm')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestPasswordResetTokenModel:
    """Тесты для модели токена сброса пароля"""

    def test_token_is_valid(self, create_user):
        """Тест проверки валидности токена"""
        user = create_user()
        
        # Создаем действующий токен
        valid_token = PasswordResetToken.objects.create(
            user=user,
            token='valid-token',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        assert valid_token.is_valid()

    def test_token_is_expired(self, create_user):
        """Тест истекшего токена"""
        user = create_user()
        
        # Создаем истекший токен
        expired_token = PasswordResetToken.objects.create(
            user=user,
            token='expired-token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        assert not expired_token.is_valid()

    def test_token_is_used(self, create_user):
        """Тест использованного токена"""
        user = create_user()
        
        # Создаем использованный токен
        used_token = PasswordResetToken.objects.create(
            user=user,
            token='used-token',
            expires_at=timezone.now() + timedelta(hours=1),
            is_used=True
        )
        
        assert not used_token.is_valid()

@pytest.mark.django_db
class TestThrottling:
    """Тесты для ограничения частоты запросов"""

    def test_anonymous_throttling(self, api_client, user_data):
        """Тест ограничения для анонимных пользователей"""
        from django.core.cache import cache
        from django.test import override_settings
        from rest_framework.throttling import AnonRateThrottle
        
        # Создаем кастомный throttle класс для тестов
        class TestAnonThrottle(AnonRateThrottle):
            rate = '2/min'
            
        cache.clear()
        
        with override_settings(
            CACHES={
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                }
            }
        ):
            # Применяем ограничение напрямую к view
            from api.users.views import UserRegistrationView
            original_throttle_classes = UserRegistrationView.throttle_classes
            UserRegistrationView.throttle_classes = [TestAnonThrottle]
            
            try:
                url = reverse('register')
                
                # Первые два запроса должны пройти
                for i in range(2):
                    user_data_copy = user_data.copy()
                    user_data_copy['email'] = f'test{i}@example.com'
                    user_data_copy['username'] = f'testuser{i}'
                    response = api_client.post(url, user_data_copy, format='json')
                    assert response.status_code == status.HTTP_201_CREATED

                # Третий запрос должен быть заблокирован
                user_data_copy = user_data.copy()
                user_data_copy['email'] = 'test3@example.com'
                user_data_copy['username'] = 'testuser3'
                response = api_client.post(url, user_data_copy, format='json')
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                
            finally:
                # Восстанавливаем оригинальные классы
                UserRegistrationView.throttle_classes = original_throttle_classes

@pytest.mark.django_db
class TestIntegration:
    """Интеграционные тесты полного рабочего процесса"""

    def test_complete_user_workflow(self, api_client, user_data):
        """Тест полного рабочего процесса пользователя"""
        # 1. Регистрация
        register_url = reverse('register')
        register_response = api_client.post(register_url, user_data, format='json')
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # 2. Получение токенов из регистрации
        access_token = register_response.data['tokens']['access']
        refresh_token = register_response.data['tokens']['refresh']
        
        # 3. Авторизуемся с полученным токеном
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 4. Получение информации об аккаунте
        account_url = reverse('account_detail')
        account_response = api_client.get(account_url)
        assert account_response.status_code == status.HTTP_200_OK
        assert account_response.data['email'] == user_data['email']
        
        # 5. Обновление профиля
        update_url = reverse('account_update')
        update_data = {'username': 'updatedusername'}
        update_response = api_client.patch(update_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        
        # 6. Смена пароля
        password_change_url = reverse('password_change')
        password_change_data = {
            'old_password': user_data['password'],
            'new_password': 'NewPassword123!'
        }
        password_response = api_client.post(password_change_url, password_change_data, format='json')
        assert password_response.status_code == status.HTTP_200_OK
        
        # 7. Выход
        logout_url = reverse('logout')
        logout_data = {'refresh': refresh_token}
        logout_response = api_client.post(logout_url, logout_data, format='json')
        assert logout_response.status_code == status.HTTP_200_OK
        
        # 8. Очищаем авторизационные данные и проверяем, что доступ запрещен
        api_client.credentials()  # Очищаем заголовки
        account_response_after_logout = api_client.get(account_url)
        assert account_response_after_logout.status_code == status.HTTP_401_UNAUTHORIZED

    def test_password_reset_workflow(self, api_client, create_user, email_backend_override):
        """Тест полного рабочего процесса сброса пароля"""
        user = create_user()
        original_password = 'TestPassword123!'
        
        # 1. Запрос на сброс пароля
        reset_url = reverse('password_reset')
        reset_data = {'email': user.email}
        reset_response = api_client.post(reset_url, reset_data, format='json')
        assert reset_response.status_code == status.HTTP_200_OK
        
        # 2. Получение токена из базы данных
        reset_token = PasswordResetToken.objects.get(user=user)
        assert reset_token.is_valid()
        
        # 3. Подтверждение сброса пароля
        confirm_url = reverse('password_reset_confirm')
        new_password = 'NewResetPassword123!'
        confirm_data = {
            'token': reset_token.token,
            'new_password': new_password
        }
        confirm_response = api_client.post(confirm_url, confirm_data, format='json')
        assert confirm_response.status_code == status.HTTP_200_OK
        
        # 4. Проверка, что пароль изменился
        user.refresh_from_db()
        assert user.check_password(new_password)
        assert not user.check_password(original_password)
        
        # 5. Проверка, что токен стал неактивным
        reset_token.refresh_from_db()
        assert not reset_token.is_valid()
