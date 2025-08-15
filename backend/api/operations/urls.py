# project/backend/api/operations/urls.py
from django.urls import path
from .views import (
    OperationListCreateView,
    OperationDetailView,
    OperationSummaryView,
    RecurringOperationListCreateView,
    RecurringOperationDetailView,
    RecurringOperationProcessView
)

urlpatterns = [
    # Основные операции
    path('operations/', OperationListCreateView.as_view(), name='operation-list'),
    path('operations/<int:pk>/', OperationDetailView.as_view(), name='operation-detail'),
    path('operations/summary/', OperationSummaryView.as_view(), name='operation-summary'),
    
    # Повторяющиеся операции
    path('recurring-operations/', RecurringOperationListCreateView.as_view(), name='recurring-operation-list'),
    path('recurring-operations/<int:pk>/', RecurringOperationDetailView.as_view(), name='recurring-operation-detail'),
    path('recurring-operations/process/', RecurringOperationProcessView.as_view(), name='recurring-operation-process'),
]
