"""
Products Models Tests - Phase 2: Product Catalog
Test Category, Product, Modifier, and related models
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import (
    Category, Product, ProductPhoto, Modifier, ModifierOption,
    ProductModifier, TableArea, Table, KitchenStation
)
from conftest import BaseTestCase


class CategoryModelTest(BaseTestCase):
    """Test Category model functionality"""
    
    def test_category_creation(self):
        """Test basic category creation"""
        category = Category.objects.create(
            brand=self.brand,
            name='Makanan',
            sort_order=1,
            icon='food-icon',
            is_active=True
        )
        
        self.assertEqual(category.brand, self.brand)
        self.assertEqual(category.name, 'Makanan')
        self.assertEqual(category.sort_order, 1)
        self.assertEqual(category.icon, 'food-icon')
        self.assertTrue(category.is_active)
        self.assertIsNone(category.parent)
    
    def test_category_hierarchical_structure(self):
        """Test hierarchical category structure"""
        parent = Category.objects.create(
            brand=self.brand,
            name='Makanan',
            sort_order=1
        )
        
        child = Category.objects.create(
            brand=self.brand,
            parent=parent,
            name='Ayam',
            sort_order=1
        )
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())
    
    def test_category_str_representation(self):
        """Test category string representation"""
        parent = Category.objects.create(brand=self.brand, name='Makanan')
        child = Category.objects.create(
            brand=self.brand,
            parent=parent,
            name='Ayam'
        )
        
        self.assertEqual(str(parent), 'Makanan')
        self.assertEqual(str(child), 'Makanan → Ayam')
    
    def test_category_cascade_delete(self):
        """Test category cascade delete with children"""
        parent = Category.objects.create(brand=self.brand, name='Makanan')
        child = Category.objects.create(
            brand=self.brand,
            parent=parent,
            name='Ayam'
        )
        
        child_id = child.id
        parent.delete()
        
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=child_id)


class ProductModelTest(BaseTestCase):
    """Test Product model functionality"""
    
    def test_product_creation(self):
        """Test basic product creation"""
        category = self.create_category()
        product = Product.objects.create(
            brand=self.brand,
            company=self.company,
            category=category,
            sku='AGE-001',
            name='Ayam Geprek Original',
            description='Ayam geprek dengan sambal terasi',
            price=Decimal('25000.00'),
            cost=Decimal('15000.00'),
            printer_target='kitchen',
            is_active=True
        )
        
        self.assertEqual(product.brand, self.brand)
        self.assertEqual(product.company, self.company)
        self.assertEqual(product.category, category)
        self.assertEqual(product.sku, 'AGE-001')
        self.assertEqual(product.name, 'Ayam Geprek Original')
        self.assertEqual(product.description, 'Ayam geprek dengan sambal terasi')
        self.assertDecimalEqual(product.price, Decimal('25000.00'))
        self.assertDecimalEqual(product.cost, Decimal('15000.00'))
        self.assertEqual(product.printer_target, 'kitchen')
        self.assertTrue(product.is_active)
    
    def test_product_sku_unique_per_brand(self):
        """Test product SKU uniqueness per brand"""
        category = self.create_category()
        
        # First product with SKU
        Product.objects.create(
            brand=self.brand,
            company=self.company,
            category=category,
            sku='AGE-001',
            name='Product 1',
            price=Decimal('25000.00'),
            cost=Decimal('15000.00')
        )
        
        # Second product with same SKU in same brand should fail
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                brand=self.brand,
                company=self.company,
                category=category,
                sku='AGE-001',
                name='Product 2',
                price=Decimal('30000.00'),
                cost=Decimal('18000.00')
            )
    
    def test_product_str_representation(self):
        """Test product string representation"""
        product = self.create_product(sku='AGE-001', name='Ayam Geprek Original')
        self.assertEqual(str(product), 'AGE-001 - Ayam Geprek Original')
    
    def test_product_margin_calculation(self):
        """Test product margin calculation"""
        product = self.create_product(price='25000.00')
        product.cost = Decimal('15000.00')
        
        expected_margin = Decimal('10000.00')  # 25000 - 15000
        expected_margin_percent = Decimal('40.00')  # (10000 / 25000) * 100
        
        self.assertDecimalEqual(product.get_margin(), expected_margin)
        self.assertDecimalEqual(product.get_margin_percent(), expected_margin_percent)
    
    def test_product_is_profitable(self):
        """Test product profitability check"""
        profitable_product = self.create_product(price='25000.00')
        profitable_product.cost = Decimal('15000.00')
        self.assertTrue(profitable_product.is_profitable())
        
        unprofitable_product = self.create_product(sku='LOSS-001', price='10000.00')
        unprofitable_product.cost = Decimal('15000.00')
        self.assertFalse(unprofitable_product.is_profitable())


class ProductPhotoModelTest(BaseTestCase):
    """Test ProductPhoto model functionality"""
    
    def test_product_photo_creation(self):
        """Test product photo creation"""
        product = self.create_product()
        
        # Create a simple test image file
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        photo = ProductPhoto.objects.create(
            product=product,
            image=image_file,
            alt_text='Test product image',
            sort_order=1,
            is_primary=True
        )
        
        self.assertEqual(photo.product, product)
        self.assertEqual(photo.alt_text, 'Test product image')
        self.assertEqual(photo.sort_order, 1)
        self.assertTrue(photo.is_primary)
    
    def test_product_photo_cascade_delete(self):
        """Test photo deletion when product is deleted"""
        product = self.create_product()
        
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        photo = ProductPhoto.objects.create(
            product=product,
            image=image_file,
            is_primary=True
        )
        
        photo_id = photo.id
        product.delete()
        
        with self.assertRaises(ProductPhoto.DoesNotExist):
            ProductPhoto.objects.get(id=photo_id)


class ModifierModelTest(BaseTestCase):
    """Test Modifier model functionality"""
    
    def test_modifier_creation(self):
        """Test basic modifier creation"""
        modifier = Modifier.objects.create(
            brand=self.brand,
            name='Level Pedas',
            modifier_type='single',
            is_required=True,
            max_selections=1,
            sort_order=1,
            is_active=True
        )
        
        self.assertEqual(modifier.brand, self.brand)
        self.assertEqual(modifier.name, 'Level Pedas')
        self.assertEqual(modifier.modifier_type, 'single')
        self.assertTrue(modifier.is_required)
        self.assertEqual(modifier.max_selections, 1)
        self.assertEqual(modifier.sort_order, 1)
        self.assertTrue(modifier.is_active)
    
    def test_modifier_str_representation(self):
        """Test modifier string representation"""
        modifier = Modifier.objects.create(
            brand=self.brand,
            name='Level Pedas',
            modifier_type='single'
        )
        self.assertEqual(str(modifier), 'Level Pedas (single)')


class ModifierOptionModelTest(BaseTestCase):
    """Test ModifierOption model functionality"""
    
    def test_modifier_option_creation(self):
        """Test basic modifier option creation"""
        modifier = Modifier.objects.create(
            brand=self.brand,
            name='Level Pedas',
            modifier_type='single'
        )
        
        option = ModifierOption.objects.create(
            modifier=modifier,
            name='Pedas Sedang',
            price=Decimal('0.00'),
            sort_order=1,
            is_active=True
        )
        
        self.assertEqual(option.modifier, modifier)
        self.assertEqual(option.name, 'Pedas Sedang')
        self.assertDecimalEqual(option.price, Decimal('0.00'))
        self.assertEqual(option.sort_order, 1)
        self.assertTrue(option.is_active)
    
    def test_modifier_option_with_price(self):
        """Test modifier option with additional price"""
        modifier = Modifier.objects.create(
            brand=self.brand,
            name='Extra Topping',
            modifier_type='multiple'
        )
        
        option = ModifierOption.objects.create(
            modifier=modifier,
            name='Extra Keju',
            price=Decimal('5000.00')
        )
        
        self.assertDecimalEqual(option.price, Decimal('5000.00'))
    
    def test_modifier_option_str_representation(self):
        """Test modifier option string representation"""
        modifier = Modifier.objects.create(brand=self.brand, name='Level Pedas')
        option = ModifierOption.objects.create(
            modifier=modifier,
            name='Pedas Sedang',
            price=Decimal('0.00')
        )
        self.assertEqual(str(option), 'Pedas Sedang (Rp 0)')


class ProductModifierModelTest(BaseTestCase):
    """Test ProductModifier relationship model"""
    
    def test_product_modifier_relationship(self):
        """Test product-modifier many-to-many relationship"""
        product = self.create_product()
        modifier = Modifier.objects.create(
            brand=self.brand,
            name='Level Pedas',
            modifier_type='single'
        )
        
        product_modifier = ProductModifier.objects.create(
            product=product,
            modifier=modifier,
            is_required=True,
            sort_order=1
        )
        
        self.assertEqual(product_modifier.product, product)
        self.assertEqual(product_modifier.modifier, modifier)
        self.assertTrue(product_modifier.is_required)
        self.assertEqual(product_modifier.sort_order, 1)
        
        # Test reverse relationships
        self.assertIn(modifier, product.modifiers.all())
        self.assertIn(product, modifier.products.all())


class TableAreaModelTest(BaseTestCase):
    """Test TableArea model functionality"""
    
    def test_table_area_creation(self):
        """Test basic table area creation"""
        table_area = TableArea.objects.create(
            brand=self.brand,
            store=self.store,
            company=self.company,
            name='Indoor Area',
            description='Area indoor dengan AC',
            capacity=50,
            sort_order=1,
            is_active=True
        )
        
        self.assertEqual(table_area.brand, self.brand)
        self.assertEqual(table_area.store, self.store)
        self.assertEqual(table_area.company, self.company)
        self.assertEqual(table_area.name, 'Indoor Area')
        self.assertEqual(table_area.description, 'Area indoor dengan AC')
        self.assertEqual(table_area.capacity, 50)
        self.assertEqual(table_area.sort_order, 1)
        self.assertTrue(table_area.is_active)
    
    def test_table_area_str_representation(self):
        """Test table area string representation"""
        table_area = TableArea.objects.create(
            brand=self.brand,
            store=self.store,
            company=self.company,
            name='Indoor Area'
        )
        self.assertEqual(str(table_area), 'Indoor Area')


class KitchenStationModelTest(BaseTestCase):
    """Test KitchenStation model functionality"""
    
    def test_kitchen_station_creation(self):
        """Test basic kitchen station creation"""
        station = KitchenStation.objects.create(
            brand=self.brand,
            store=self.store,
            name='Grill Station',
            description='Station untuk grilling',
            printer_ip='192.168.1.100',
            is_active=True
        )
        
        self.assertEqual(station.brand, self.brand)
        self.assertEqual(station.store, self.store)
        self.assertEqual(station.name, 'Grill Station')
        self.assertEqual(station.description, 'Station untuk grilling')
        self.assertEqual(station.printer_ip, '192.168.1.100')
        self.assertTrue(station.is_active)
    
    def test_kitchen_station_str_representation(self):
        """Test kitchen station string representation"""
        station = KitchenStation.objects.create(
            brand=self.brand,
            store=self.store,
            name='Grill Station'
        )
        self.assertEqual(str(station), 'Grill Station')


@pytest.mark.unit
class CategoryModelPyTest:
    """Pytest version of Category model tests"""
    
    def test_category_creation(self, category):
        """Test category creation with fixture"""
        assert category.name == 'Test Category'
        assert category.is_active is True
    
    def test_category_hierarchy(self, brand):
        """Test category hierarchical structure"""
        parent = Category.objects.create(brand=brand, name='Parent')
        child = Category.objects.create(brand=brand, parent=parent, name='Child')
        
        assert child.parent == parent
        assert child in parent.children.all()


@pytest.mark.unit
class ProductModelPyTest:
    """Pytest version of Product model tests"""
    
    def test_product_creation(self, product):
        """Test product creation with fixture"""
        assert product.sku == 'TEST-001'
        assert product.name == 'Test Product'
        assert product.is_active is True
    
    def test_product_margin_calculation(self, product):
        """Test product margin calculation"""
        product.price = Decimal('25000.00')
        product.cost = Decimal('15000.00')
        
        assert product.get_margin() == Decimal('10000.00')
        assert product.get_margin_percent() == Decimal('40.00')


@pytest.mark.unit
class ModifierModelPyTest:
    """Pytest version of Modifier model tests"""
    
    def test_modifier_creation(self, modifier):
        """Test modifier creation with fixture"""
        assert modifier.name == 'Test Modifier'
        assert modifier.modifier_type == 'single'
        assert modifier.is_active is True
    
    def test_modifier_option_creation(self, modifier_option):
        """Test modifier option creation with fixture"""
        assert modifier_option.name == 'Test Option'
        assert modifier_option.price == Decimal('5000.00')
        assert modifier_option.is_active is True
