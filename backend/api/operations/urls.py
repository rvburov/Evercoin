# project/backend/api/operations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperationViewSet

router = DefaultRouter()
router.register(r'operations', OperationViewSet, basename='operation')

urlpatterns = [
    path('api/', include(router.urls)),
]
