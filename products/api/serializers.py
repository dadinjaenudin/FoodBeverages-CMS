"""
Products API Serializers - For HO → Edge Sync
"""
from rest_framework import serializers
from products.models import (
    Category, Product, ProductPhoto, Modifier, ModifierOption,
    ProductModifier, TableArea, Table, KitchenStation, PrinterConfig
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ModifierOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModifierOption
        fields = '__all__'
        read_only_fields = ['id']


class ModifierSerializer(serializers.ModelSerializer):
    options = ModifierOptionSerializer(many=True, read_only=True, source='modifieroption_set')
    
    class Meta:
        model = Modifier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductModifierSerializer(serializers.ModelSerializer):
    modifier_details = ModifierSerializer(source='modifier', read_only=True)
    
    class Meta:
        model = ProductModifier
        fields = ['id', 'product', 'modifier', 'modifier_details']


class ProductSerializer(serializers.ModelSerializer):
    photos = ProductPhotoSerializer(many=True, read_only=True, source='productphoto_set')
    modifiers = ProductModifierSerializer(many=True, read_only=True, source='productmodifier_set')
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TableAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableArea
        fields = '__all__'
        read_only_fields = ['id']


class TableSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    
    class Meta:
        model = Table
        fields = ['id', 'area', 'area_name', 'number', 'capacity', 'qr_code', 'pos_x', 'pos_y']
        # Note: status and table_group_id are managed by Edge, not synced from HO


class KitchenStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenStation
        fields = '__all__'
        read_only_fields = ['id']


class PrinterConfigSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = PrinterConfig
        fields = '__all__'
        read_only_fields = ['id']
