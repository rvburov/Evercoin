# evercoin/backend/api/categories/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryBudgetViewSet,
    CategoryConstantsViewSet,
    CategoryViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(
    r'budgets',
    CategoryBudgetViewSet,
    basename='category-budget'
)
router.register(
    r'constants',
    CategoryConstantsViewSet,
    basename='category-constants'
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'categories/tree/',
        CategoryViewSet.as_view({'get': 'tree'}),
        name='category-tree'
    ),
    path(
        'categories/type/<str:type>/',
        CategoryViewSet.as_view({'get': 'by_type'}),
        name='category-by-type'
    ),
    path(
        'categories/analytics/',
        CategoryViewSet.as_view({'get': 'analytics'}),
        name='category-analytics'
    ),
    path(
        'budgets/active/',
        CategoryBudgetViewSet.as_view({'get': 'active'}),
        name='category-budget-active'
    ),
    path(
        'budgets/overview/',
        CategoryBudgetViewSet.as_view({'get': 'overview'}),
        name='category-budget-overview'
    ),
]