# project/backend/api/categories/urls.py
from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    category_tree
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/tree/', category_tree, name='category-tree'),
]
