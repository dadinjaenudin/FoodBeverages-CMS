"""
Transactions API URLs - Edge → HO Push
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BillPushViewSet, CashDropPushViewSet, StoreSessionPushViewSet,
    CashierShiftPushViewSet, InventoryMovementPushViewSet, bulk_push
)

router = DefaultRouter()
router.register(r'bills', BillPushViewSet, basename='bill-push')
router.register(r'cash-drops', CashDropPushViewSet, basename='cashdrop-push')
router.register(r'sessions', StoreSessionPushViewSet, basename='session-push')
router.register(r'shifts', CashierShiftPushViewSet, basename='shift-push')
router.register(r'inventory', InventoryMovementPushViewSet, basename='inventory-push')

urlpatterns = [
    path('', include(router.urls)),
    path('bulk-push/', bulk_push, name='bulk-push'),
]
