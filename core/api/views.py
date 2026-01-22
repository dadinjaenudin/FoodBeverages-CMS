"""
Core API Views - Master Data Sync Endpoints
HO → Edge: Master data pull by Edge servers
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from core.models import Company, Brand, Store, User
from .serializers import (
    CompanySerializer, BrandSerializer, StoreSerializer, UserSerializer
)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Company master data - Edge pulls company info
    READ-ONLY for Edge
    """
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync endpoint for Edge to pull company data
        Query params: last_sync (ISO datetime)
        """
        last_sync = request.query_params.get('last_sync')
        queryset = self.get_queryset()
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Brand master data - Edge pulls brand configuration
    READ-ONLY for Edge
    """
    queryset = Brand.objects.select_related('company').filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync endpoint for Edge to pull brand data
        Query params: 
          - brand_id: specific brand (required for Edge)
          - last_sync: ISO datetime
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id=brand_id)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Store master data - Edge pulls own store configuration
    READ-ONLY for Edge
    """
    queryset = Store.objects.select_related('brand__company').filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync endpoint for Edge to pull store data
        Query params:
          - store_id: specific store (required for Edge)
          - last_sync: ISO datetime
        """
        store_id = request.query_params.get('store_id')
        last_sync = request.query_params.get('last_sync')
        
        if not store_id:
            return Response(
                {'error': 'store_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id=store_id)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User master data - Edge pulls authorized users
    READ-ONLY for Edge
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync endpoint for Edge to pull user data
        Query params:
          - brand_id: filter users for brand
          - last_sync: ISO datetime
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get users: brand-specific OR company-wide
        queryset = self.get_queryset().filter(
            models.Q(brand_id=brand_id) | models.Q(role_scope='company')
        )
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
