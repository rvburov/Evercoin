# evercoin/backend/api/wallets/apps.py
from django.apps import AppConfig


class WalletsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.wallets'
    verbose_name = 'Финансовые счета'
