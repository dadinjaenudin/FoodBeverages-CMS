"""
Promotions API Serializers - For HO → Edge Sync
Complex serialization due to M2M relationships and nested data
"""
from rest_framework import serializers
from promotions.models import (
    Promotion, PackagePromotion, PackageItem, PromotionTier,
    Voucher, PromotionUsage
)


class PackageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageItem
        fields = '__all__'
        read_only_fields = ['id']


class PackagePromotionSerializer(serializers.ModelSerializer):
    items = PackageItemSerializer(many=True, read_only=True, source='packageitem_set')
    
    class Meta:
        model = PackagePromotion
        fields = '__all__'
        read_only_fields = ['id']


class PromotionTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionTier
        fields = '__all__'
        read_only_fields = ['id']


class PromotionSerializer(serializers.ModelSerializer):
    package = PackagePromotionSerializer(read_only=True, source='packagepromotion')
    tiers = PromotionTierSerializer(many=True, read_only=True, source='promotiontier_set')
    
    # M2M relationships - return IDs only for sync efficiency
    brand_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source='brands'
    )
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source='products'
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source='categories'
    )
    exclude_product_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source='exclude_products'
    )
    exclude_category_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source='exclude_categories'
    )
    
    class Meta:
        model = Promotion
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class VoucherSerializer(serializers.ModelSerializer):
    promotion_name = serializers.CharField(source='promotion.name', read_only=True)
    
    class Meta:
        model = Voucher
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PromotionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionUsage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
