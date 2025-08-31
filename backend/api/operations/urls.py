# evercoin/backend/api/operations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OperationViewSet, OperationLogViewSet

router = DefaultRouter()
# Базовые CRUD 
router.register(
    r'operations',
    OperationViewSet,
    basename='operation'
)
# Логирование
router.register(
    r'operation-logs',
    OperationLogViewSet,
    basename='operation-log'
)

urlpatterns = [

    path('', include(router.urls)),

    # Фильтрация и пагинация
    path(
        'operations/list/',
        OperationViewSet.as_view({'get': 'list_operations'}),
        name='operation-list-filtered'
    ),

    # Операции по типам
    path(
        'operations/income/',
        OperationViewSet.as_view({'get': 'income_operations'}),
        name='operation-income'
    ),
    path(
        'operations/expense/',
        OperationViewSet.as_view({'get': 'expense_operations'}),
        name='operation-expense'
    ),

    # Аналитика и отчеты
    path(
        'operations/analytics/financial/',
        OperationViewSet.as_view({'get': 'financial_analytics'}),
        name='operation-analytics-financial'
    ),
    path(
        'operations/daily-result/',
        OperationViewSet.as_view({'get': 'daily_financial_result'}),
        name='operation-daily-result'
    ),
]