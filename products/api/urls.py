"""
Products API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, ModifierViewSet,
    TableAreaViewSet, TableViewSet, KitchenStationViewSet, PrinterConfigViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'modifiers', ModifierViewSet, basename='modifier')
router.register(r'table-areas', TableAreaViewSet, basename='tablearea')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'kitchen-stations', KitchenStationViewSet, basename='kitchenstation')
router.register(r'printers', PrinterConfigViewSet, basename='printerconfig')

urlpatterns = [
    path('', include(router.urls)),
]
