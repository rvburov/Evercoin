# evercoin/backend/api/categories/urls.py
from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # Список категорий
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Детали категории
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Создание категории
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    
    # Обновление категории
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    
    # Удаление категории
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    
    # Слияние категорий
    path('categories/merge/', views.CategoryMergeView.as_view(), name='category-merge'),
    
    # Массовое создание категорий
    path('categories/bulk-create/', views.CategoryBulkCreateView.as_view(), name='category-bulk-create'),
    
    # Категории по типу
    path('categories/type/<str:type>/', views.CategoryByTypeView.as_view(), name='category-by-type'),
    
    # Активация/деактивация категории
    path('categories/<int:pk>/toggle-active/', views.CategoryToggleActiveView.as_view(), name='category-toggle-active'),
    
    # Системные категории
    path('categories/default/', views.CategoryDefaultListView.as_view(), name='category-default-list'),
    
    # Создание стандартных категорий
    path('categories/create-default/', views.create_default_categories, name='create-default-categories'),
    
    # Статистика по категориям
    path('categories/statistics/', views.category_statistics, name='category-statistics'),
]