"""
Inventory & Recipe Management Models
Based on LLM_MASTER_PROMPT_FNB_INVENTORY.md
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Brand, Store, User
from products.models import Product


class InventoryItem(models.Model):
    """
    Inventory Item - Raw materials, semi-finished, finished goods, packaging
    """
    ITEM_TYPE_CHOICES = [
        ('raw_material', 'Raw Material'),
        ('semi_finished', 'Semi-Finished'),
        ('finished_goods', 'Finished Goods'),
        ('packaging', 'Packaging'),
    ]
    
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('gram', 'Gram'),
        ('liter', 'Liter'),
        ('ml', 'Milliliter'),
        ('pcs', 'Pieces'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='inventory_items')
    item_code = models.CharField(max_length=50, help_text="Unique per brand")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    base_unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    conversion_factor = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1,
        help_text="e.g., 1 kg = 1000 gram"
    )
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="For FIFO costing"
    )
    track_stock = models.BooleanField(default=True)
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_item'
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        ordering = ['name']
        unique_together = [['brand', 'item_code']]
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['item_code']),
            models.Index(fields=['item_type']),
        ]
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"


class Recipe(models.Model):
    """
    Recipe (BOM - Bill of Materials)
    Links menu item to ingredients
    """
    PREPARATION_TYPE_CHOICES = [
        ('prep', 'Preparation'),
        ('cook', 'Cooking'),
        ('fry', 'Frying'),
        ('assemble', 'Assembly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='recipes')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='recipes')
    recipe_code = models.CharField(max_length=50)
    recipe_name = models.CharField(max_length=200)
    version = models.IntegerField(default=1, help_text="Recipe versioning")
    yield_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Output quantity per batch")
    yield_unit = models.CharField(max_length=20)
    preparation_type = models.CharField(max_length=20, choices=PREPARATION_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recipe'
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-version']
        unique_together = [['brand', 'product', 'version']]
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['product', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.recipe_code} - {self.recipe_name} (v{self.version})"


class RecipeIngredient(models.Model):
    """
    Recipe Ingredient - Components of a recipe
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='recipe_uses')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=20)
    yield_factor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Loss during prep/cook (e.g., 0.70 = 30% loss)"
    )
    is_critical = models.BooleanField(default=False, help_text="Cannot substitute")
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'recipe_ingredient'
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipe Ingredients'
        ordering = ['sort_order']
        indexes = [
            models.Index(fields=['recipe']),
            models.Index(fields=['inventory_item']),
        ]
    
    def __str__(self):
        return f"{self.recipe.recipe_name} - {self.inventory_item.name}"


# Note: InventoryMovement, ManufacturingOrder, StockLocation, etc. 
# will be managed by Edge Server and synced to HO for reporting
# HO stores master data only


class StockMovement(models.Model):
    """
    Stock Movement - Track inventory changes
    Read-only in HO, synced from Edge servers
    """
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('production', 'Production Use'),
        ('waste', 'Waste/Spoilage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='stock_movements')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=20)
    reference_no = models.CharField(max_length=100, blank=True, help_text="PO/SO/Transfer number")
    notes = models.TextField(blank=True)
    movement_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_movement'
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['store', 'movement_date']),
            models.Index(fields=['inventory_item', 'movement_date']),
            models.Index(fields=['movement_type']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.inventory_item.name} ({self.quantity} {self.unit})"
