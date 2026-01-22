"""
Inventory API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, RecipeViewSet

router = DefaultRouter()
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
