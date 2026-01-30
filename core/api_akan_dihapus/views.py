"""
Core API Views - Master Data Endpoints
HO → Edge: Master data pull by Edge servers
"""
from rest_framework import viewsets, permissions
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


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Brand master data - Edge pulls brand configuration
    READ-ONLY for Edge
    """
    queryset = Brand.objects.select_related('company').filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Store master data - Edge pulls own store configuration
    READ-ONLY for Edge
    """
    queryset = Store.objects.select_related('brand__company').filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User master data - Edge pulls authorized users
    READ-ONLY for Edge
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
