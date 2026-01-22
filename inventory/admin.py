"""
Admin configuration for Inventory app
"""

from django.contrib import admin
from .models import InventoryItem, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['inventory_item']
    fields = ['inventory_item', 'quantity', 'unit', 'yield_factor', 'is_critical', 'sort_order']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'brand', 'item_type', 'base_unit', 'cost_per_unit', 'is_active']
    list_filter = ['brand', 'item_type', 'base_unit', 'is_active']
    search_fields = ['item_code', 'name', 'brand__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['brand']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'brand', 'item_code', 'name', 'description', 'item_type', 'is_active')
        }),
        ('Unit & Costing', {
            'fields': ('base_unit', 'conversion_factor', 'cost_per_unit')
        }),
        ('Stock Management', {
            'fields': ('track_stock', 'min_stock', 'max_stock')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['recipe_code', 'recipe_name', 'brand', 'product', 'version', 'is_active', 'effective_date']
    list_filter = ['brand', 'preparation_type', 'is_active', 'effective_date']
    search_fields = ['recipe_code', 'recipe_name', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['brand', 'product']
    inlines = [RecipeIngredientInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'brand', 'product', 'recipe_code', 'recipe_name', 'version', 'is_active')
        }),
        ('Yield', {
            'fields': ('yield_quantity', 'yield_unit', 'preparation_type')
        }),
        ('Versioning', {
            'fields': ('effective_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'inventory_item', 'quantity', 'unit', 'yield_factor', 'is_critical']
    list_filter = ['recipe__brand', 'is_critical']
    search_fields = ['recipe__recipe_name', 'inventory_item__name']
    readonly_fields = ['id']
    autocomplete_fields = ['recipe', 'inventory_item']
