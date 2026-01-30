"""
Core API Serializers - For HO → Edge Sync (Master Data Pull)
"""
from rest_framework import serializers
from core.models import Company, Brand, Store, User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class StoreSerializer(serializers.ModelSerializer):
    company_id = serializers.SerializerMethodField()
    brand_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Store
        fields = [
            'id', 'company_id', 'brand_id', 'store_code', 'store_name',
            'address', 'phone', 'timezone', 'latitude', 'longitude',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_company_id(self, obj):
        """
        Get company_id through brand relation
        Returns None if brand or company doesn't exist
        """
        try:
            if obj.brand and obj.brand.company:
                return str(obj.brand.company.id)
        except Exception:
            pass
        return None
    
    def get_brand_id(self, obj):
        """
        Get brand_id
        Returns None if brand doesn't exist
        """
        try:
            if obj.brand:
                return str(obj.brand.id)
        except Exception:
            pass
        return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'company_id', 'role', 'role_scope', 'pin',
            'profile_photo', 'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}
