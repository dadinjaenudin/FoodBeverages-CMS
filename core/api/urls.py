"""
Core API URLs - Master Data Sync Endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, BrandViewSet, StoreViewSet, UserViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
