"""
Inventory API Views - HO → Edge Sync
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Prefetch
from inventory.models import InventoryItem, Recipe, RecipeIngredient
from .serializers import InventoryItemSerializer, RecipeSerializer


class InventoryItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Inventory item master data - Edge pulls items"""
    queryset = InventoryItem.objects.filter(is_active=True)
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync inventory items for specific brand
        Query params: brand_id, last_sync, item_type (optional)
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        item_type = request.query_params.get('item_type')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(brand_id=brand_id)
        
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """Recipe master data - Edge pulls active recipes with ingredients"""
    queryset = Recipe.objects.select_related('product', 'brand').prefetch_related(
        Prefetch('recipeingredient_set', queryset=RecipeIngredient.objects.select_related('inventory_item').order_by('sort_order'))
    ).filter(is_active=True)
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync recipes for specific brand
        Query params: brand_id, last_sync, product_id (optional)
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        product_id = request.query_params.get('product_id')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(brand_id=brand_id)
        
        # Filter by product if specified
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Incremental sync
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        # Filter to only return active recipes (latest version per product)
        # This is a simplification - in production, you'd handle versioning more robustly
        queryset = queryset.filter(
            end_date__isnull=True
        ) | queryset.filter(
            end_date__gte=timezone.now().date()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Get active recipe for specific product
        Query params: product_id
        """
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the active recipe for this product
        now = timezone.now().date()
        recipe = self.get_queryset().filter(
            product_id=product_id,
            effective_date__lte=now
        ).filter(
            end_date__isnull=True
        ) | self.get_queryset().filter(
            product_id=product_id,
            effective_date__lte=now,
            end_date__gte=now
        )
        
        recipe = recipe.first()
        
        if not recipe:
            return Response(
                {'error': 'No active recipe found for this product'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)
