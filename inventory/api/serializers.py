"""
Inventory API Serializers - For HO → Edge Sync
"""
from rest_framework import serializers
from inventory.models import InventoryItem, Recipe, RecipeIngredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='inventory_item.name', read_only=True)
    item_code = serializers.CharField(source='inventory_item.item_code', read_only=True)
    
    class Meta:
        model = RecipeIngredient
        fields = '__all__'
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipeingredient_set')
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
