# evercoin/backend/api/operations/urls.py
from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Список операций с фильтрацией и пагинацией
    path('operations/', views.OperationListView.as_view(), name='operation-list'),
    
    # Детали операции
    path('operations/<int:pk>/', views.OperationDetailView.as_view(), name='operation-detail'),
    
    # Создание операции
    path('operations/create/', views.OperationCreateView.as_view(), name='operation-create'),
    
    # Обновление операции
    path('operations/<int:pk>/update/', views.OperationUpdateView.as_view(), name='operation-update'),
    
    # Удаление операции
    path('operations/<int:pk>/delete/', views.OperationDeleteView.as_view(), name='operation-delete'),
    
    # Копирование операции
    path('operations/<int:pk>/copy/', views.OperationCopyView.as_view(), name='operation-copy'),
    
    # Массовое удаление операций
    path('operations/bulk-delete/', views.OperationBulkDeleteView.as_view(), name='operation-bulk-delete'),
]
