from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OperationViewSet

router = DefaultRouter()
router.register(r'operations', OperationViewSet, basename='operation')

urlpatterns = [
    path('operations/analytics/', OperationViewSet.as_view({'get': 'analytics'}), name='operations-analytics'),
    path('operations/by-category/', OperationViewSet.as_view({'get': 'by_category'}), name='operations-by-category'),
] + router.urls
