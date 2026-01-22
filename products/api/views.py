"""
Products API Views - Master Data Sync Endpoints
HO → Edge: Products, Categories, Modifiers, Tables
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Prefetch
from products.models import (
    Category, Product, ProductPhoto, Modifier, ModifierOption,
    ProductModifier, TableArea, Table, KitchenStation, PrinterConfig
)
from .serializers import (
    CategorySerializer, ProductSerializer, ModifierSerializer,
    TableAreaSerializer, TableSerializer, KitchenStationSerializer,
    PrinterConfigSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Category master data - Edge pulls categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync categories for specific brand
        Query params: brand_id, last_sync
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(brand_id=brand_id)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Product master data - Edge pulls products with photos & modifiers"""
    queryset = Product.objects.select_related('category', 'brand').prefetch_related(
        'productphoto_set',
        Prefetch('productmodifier_set', queryset=ProductModifier.objects.select_related('modifier'))
    ).filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync products for specific brand
        Query params: brand_id, last_sync, category_id (optional)
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        category_id = request.query_params.get('category_id')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(brand_id=brand_id)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class ModifierViewSet(viewsets.ReadOnlyModelViewSet):
    """Modifier master data - Edge pulls modifiers with options"""
    queryset = Modifier.objects.prefetch_related('modifieroption_set').filter(is_active=True)
    serializer_class = ModifierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync modifiers for specific brand
        Query params: brand_id, last_sync
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(brand_id=brand_id)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class TableAreaViewSet(viewsets.ReadOnlyModelViewSet):
    """Table area master data"""
    queryset = TableArea.objects.filter(is_active=True)
    serializer_class = TableAreaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """Sync table areas for specific brand"""
        brand_id = request.query_params.get('brand_id')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(brand_id=brand_id)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class TableViewSet(viewsets.ReadOnlyModelViewSet):
    """Table master data (template only, status managed by Edge)"""
    queryset = Table.objects.select_related('area')
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """Sync tables for specific brand"""
        brand_id = request.query_params.get('brand_id')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(area__brand_id=brand_id)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class KitchenStationViewSet(viewsets.ReadOnlyModelViewSet):
    """Kitchen station master data"""
    queryset = KitchenStation.objects.filter(is_active=True)
    serializer_class = KitchenStationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """Sync kitchen stations (company-wide or brand-specific)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class PrinterConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """Printer config master data"""
    queryset = PrinterConfig.objects.select_related('station').filter(is_active=True)
    serializer_class = PrinterConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """Sync printer configs"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
