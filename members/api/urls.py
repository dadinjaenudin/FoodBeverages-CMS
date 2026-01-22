"""
Members API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, MemberTransactionViewSet

router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'transactions', MemberTransactionViewSet, basename='membertransaction')

urlpatterns = [
    path('', include(router.urls)),
]
