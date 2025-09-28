# evercoin/backend/api/analytics/apps.py
from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.analytics'
    verbose_name = 'Аналитика'
