"""
Promotions API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromotionViewSet, VoucherViewSet, PromotionUsageViewSet

router = DefaultRouter()
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'vouchers', VoucherViewSet, basename='voucher')
router.register(r'usage', PromotionUsageViewSet, basename='promotionusage')

urlpatterns = [
    path('', include(router.urls)),
]
