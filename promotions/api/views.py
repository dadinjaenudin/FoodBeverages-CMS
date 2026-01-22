"""
Promotions API Views - HO → Edge Sync
Complex filtering based on scope, date range, brand, etc.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Prefetch
from promotions.models import (
    Promotion, PackagePromotion, PackageItem, PromotionTier,
    Voucher, PromotionUsage
)
from .serializers import (
    PromotionSerializer, VoucherSerializer, PromotionUsageSerializer
)


class PromotionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Promotion master data - Edge pulls active promotions
    Complex filtering: scope, brand, date range, channel
    """
    queryset = Promotion.objects.select_related(
        'company', 'brand', 'packagepromotion'
    ).prefetch_related(
        'brands', 'products', 'categories',
        'exclude_products', 'exclude_categories',
        'promotiontier_set',
        Prefetch('packagepromotion__packageitem_set', queryset=PackageItem.objects.order_by('sort_order'))
    ).filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync promotions for specific brand/store
        Query params:
          - brand_id: required
          - last_sync: ISO datetime (optional)
          - channel: DINE_IN/TAKEAWAY/DELIVERY/QRORDER (optional)
        
        Returns promotions with scope:
          - company (all brands)
          - brand (specific brand)
          - multi-brand (if brand_id in brands)
        """
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        channel = request.query_params.get('channel')
        
        if not brand_id:
            return Response(
                {'error': 'brand_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current datetime for date range filtering
        now = timezone.now()
        
        # Build query: scope filtering
        queryset = self.get_queryset().filter(
            Q(scope='company') |  # Company-wide
            Q(scope='brand', brand_id=brand_id) |  # Brand-specific
            Q(scope='multi_brand', brands__id=brand_id)  # Multi-brand
        ).filter(
            start_date__lte=now,
            end_date__gte=now
        ).distinct()
        
        # Channel filtering
        if channel:
            queryset = queryset.filter(
                Q(channel__contains=[channel]) | Q(channel__isnull=True) | Q(channel=[])
            )
        
        # Incremental sync
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def check_eligibility(self, request, pk=None):
        """
        Check promotion eligibility for specific bill context
        Query params: subtotal, member_id, customer_phone, channel
        """
        promotion = self.get_object()
        
        # TODO: Implement full eligibility check logic
        # This would check:
        # - Date/time rules
        # - Min purchase
        # - Min quantity
        # - Customer eligibility (member tier, first order, etc.)
        # - Usage limits
        # - Product/category requirements
        
        return Response({
            'promotion_id': promotion.id,
            'eligible': True,  # Simplified for now
            'reason': 'Eligibility check not fully implemented'
        })


class VoucherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Voucher master data - Edge pulls active vouchers
    Bidirectional: Edge marks voucher as used
    """
    queryset = Voucher.objects.select_related('promotion').filter(
        status='ACTIVE'
    )
    serializer_class = VoucherSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync active vouchers
        Query params: customer_phone (optional), last_sync (optional)
        """
        customer_phone = request.query_params.get('customer_phone')
        last_sync = request.query_params.get('last_sync')
        
        queryset = self.get_queryset().filter(
            expires_at__gte=timezone.now()
        )
        
        if customer_phone:
            queryset = queryset.filter(customer_phone=customer_phone)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """
        Validate voucher code
        Body: { code }
        """
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'code required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            voucher = Voucher.objects.select_related('promotion').get(
                code=code,
                status='ACTIVE',
                expires_at__gte=timezone.now()
            )
            serializer = self.get_serializer(voucher)
            return Response({
                'valid': True,
                'voucher': serializer.data
            })
        except Voucher.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid or expired voucher'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def mark_used(self, request, pk=None):
        """
        Mark voucher as used (from Edge after bill paid)
        Body: { used_by, used_bill }
        """
        voucher = self.get_object()
        
        if voucher.status != 'ACTIVE':
            return Response(
                {'error': 'Voucher already used or expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        voucher.status = 'USED'
        voucher.used_at = timezone.now()
        voucher.used_by = request.data.get('used_by')
        voucher.used_bill = request.data.get('used_bill')
        voucher.save(update_fields=['status', 'used_at', 'used_by', 'used_bill'])
        
        serializer = self.get_serializer(voucher)
        return Response(serializer.data)


class PromotionUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Promotion usage tracking - Read-only for reporting
    Edge creates usage records via separate push endpoint
    """
    queryset = PromotionUsage.objects.select_related('promotion', 'member').all()
    serializer_class = PromotionUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def check_limit(self, request):
        """
        Check if customer has reached usage limit for promotion
        Query params: promotion_id, member_id or customer_phone
        """
        promotion_id = request.query_params.get('promotion_id')
        member_id = request.query_params.get('member_id')
        customer_phone = request.query_params.get('customer_phone')
        
        if not promotion_id:
            return Response(
                {'error': 'promotion_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from promotions.models import Promotion
            promotion = Promotion.objects.get(id=promotion_id)
        except Promotion.DoesNotExist:
            return Response(
                {'error': 'Promotion not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check usage count
        queryset = self.get_queryset().filter(promotion_id=promotion_id)
        
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        elif customer_phone:
            queryset = queryset.filter(customer_phone=customer_phone)
        else:
            return Response(
                {'error': 'member_id or customer_phone required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usage_count = queryset.count()
        max_usage = promotion.max_usage_per_customer or 999999
        
        return Response({
            'promotion_id': promotion_id,
            'usage_count': usage_count,
            'max_usage': max_usage,
            'limit_reached': usage_count >= max_usage,
            'remaining': max(0, max_usage - usage_count)
        })
