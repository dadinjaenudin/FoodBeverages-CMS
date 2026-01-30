"""
Core Models Tests - Phase 1: Foundation
Test multi-tenant hierarchy: Company → Brand → Store → User
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

from core.models import Company, Brand, Store
from conftest import BaseTestCase

User = get_user_model()


class CompanyModelTest(BaseTestCase):
    """Test Company model functionality"""
    
    def test_company_creation(self):
        """Test basic company creation"""
        company = Company.objects.create(
            code='YGY',
            name='Yogya Group',
            timezone='Asia/Jakarta',
            point_expiry_months=12,
            points_per_currency=Decimal('1.00')
        )
        
        self.assertEqual(company.code, 'YGY')
        self.assertEqual(company.name, 'Yogya Group')
        self.assertEqual(company.timezone, 'Asia/Jakarta')
        self.assertEqual(company.point_expiry_months, 12)
        self.assertDecimalEqual(company.points_per_currency, Decimal('1.00'))
        self.assertTrue(company.is_active)
        self.assertIsNotNone(company.id)
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)
    
    def test_company_code_unique(self):
        """Test company code uniqueness constraint"""
        Company.objects.create(code='YGY', name='Yogya Group 1')
        
        with self.assertRaises(IntegrityError):
            Company.objects.create(code='YGY', name='Yogya Group 2')
    
    def test_company_str_representation(self):
        """Test company string representation"""
        company = Company.objects.create(code='YGY', name='Yogya Group')
        self.assertEqual(str(company), 'YGY - Yogya Group')
    
    def test_get_point_expiry_months(self):
        """Test point expiry months getter"""
        company = Company.objects.create(
            code='YGY',
            name='Yogya Group',
            point_expiry_months=24
        )
        self.assertEqual(company.get_point_expiry_months(), 24)
    
    def test_company_defaults(self):
        """Test company default values"""
        company = Company.objects.create(code='TEST', name='Test Company')
        
        self.assertEqual(company.timezone, 'Asia/Jakarta')
        self.assertEqual(company.point_expiry_months, 12)
        self.assertDecimalEqual(company.points_per_currency, Decimal('1.00'))
        self.assertTrue(company.is_active)


class BrandModelTest(BaseTestCase):
    """Test Brand model functionality"""
    
    def test_brand_creation(self):
        """Test basic brand creation"""
        brand = Brand.objects.create(
            company=self.company,
            code='YGY-001',
            name='Ayam Geprek Express',
            address='Jl. Test No. 123',
            phone='021-12345678',
            tax_id='12.345.678.9-012.000',
            tax_rate=Decimal('11.00'),
            service_charge=Decimal('5.00')
        )
        
        self.assertEqual(brand.company, self.company)
        self.assertEqual(brand.code, 'YGY-001')
        self.assertEqual(brand.name, 'Ayam Geprek Express')
        self.assertEqual(brand.address, 'Jl. Test No. 123')
        self.assertEqual(brand.phone, '021-12345678')
        self.assertEqual(brand.tax_id, '12.345.678.9-012.000')
        self.assertDecimalEqual(brand.tax_rate, Decimal('11.00'))
        self.assertDecimalEqual(brand.service_charge, Decimal('5.00'))
        self.assertTrue(brand.is_active)
    
    def test_brand_company_cascade_delete(self):
        """Test brand deletion when company is deleted"""
        brand = Brand.objects.create(
            company=self.company,
            code='YGY-001',
            name='Test Brand'
        )
        
        brand_id = brand.id
        self.company.delete()
        
        with self.assertRaises(Brand.DoesNotExist):
            Brand.objects.get(id=brand_id)
    
    def test_brand_str_representation(self):
        """Test brand string representation"""
        brand = Brand.objects.create(
            company=self.company,
            code='YGY-001',
            name='Ayam Geprek Express'
        )
        self.assertEqual(str(brand), 'YGY-001 - Ayam Geprek Express')
    
    def test_brand_get_point_expiry_months_override(self):
        """Test brand point expiry override"""
        brand = Brand.objects.create(
            company=self.company,
            code='YGY-001',
            name='Test Brand',
            point_expiry_months_override=6
        )
        self.assertEqual(brand.get_point_expiry_months(), 6)
    
    def test_brand_get_point_expiry_months_company_default(self):
        """Test brand uses company default when no override"""
        brand = Brand.objects.create(
            company=self.company,
            code='YGY-001',
            name='Test Brand'
        )
        self.assertEqual(brand.get_point_expiry_months(), self.company.point_expiry_months)
    
    def test_brand_defaults(self):
        """Test brand default values"""
        brand = Brand.objects.create(
            company=self.company,
            code='YGY-001',
            name='Test Brand'
        )
        
        self.assertDecimalEqual(brand.tax_rate, Decimal('11.00'))
        self.assertDecimalEqual(brand.service_charge, Decimal('5.00'))
        self.assertTrue(brand.is_active)
        self.assertIsNone(brand.point_expiry_months_override)


class StoreModelTest(BaseTestCase):
    """Test Store model functionality"""
    
    def test_store_creation(self):
        """Test basic store creation"""
        store = Store.objects.create(
            brand=self.brand,
            code='YGY-001-001',
            name='BSD Store',
            address='Jl. BSD Raya No. 123',
            phone='021-87654321',
            timezone='Asia/Jakarta',
            latitude=Decimal('-6.2088'),
            longitude=Decimal('106.8456')
        )
        
        self.assertEqual(store.brand, self.brand)
        self.assertEqual(store.code, 'YGY-001-001')
        self.assertEqual(store.name, 'BSD Store')
        self.assertEqual(store.address, 'Jl. BSD Raya No. 123')
        self.assertEqual(store.phone, '021-87654321')
        self.assertEqual(store.timezone, 'Asia/Jakarta')
        self.assertDecimalEqual(store.latitude, Decimal('-6.2088'))
        self.assertDecimalEqual(store.longitude, Decimal('106.8456'))
        self.assertTrue(store.is_active)
    
    def test_store_brand_cascade_delete(self):
        """Test store deletion when brand is deleted"""
        store = Store.objects.create(
            brand=self.brand,
            code='YGY-001-001',
            name='Test Store'
        )
        
        store_id = store.id
        self.brand.delete()
        
        with self.assertRaises(Store.DoesNotExist):
            Store.objects.get(id=store_id)
    
    def test_store_str_representation(self):
        """Test store string representation"""
        store = Store.objects.create(
            brand=self.brand,
            code='YGY-001-001',
            name='BSD Store'
        )
        self.assertEqual(str(store), 'YGY-001-001 - BSD Store')
    
    def test_store_defaults(self):
        """Test store default values"""
        store = Store.objects.create(
            brand=self.brand,
            code='YGY-001-001',
            name='Test Store'
        )
        
        self.assertEqual(store.timezone, 'Asia/Jakarta')
        self.assertTrue(store.is_active)
        self.assertIsNone(store.latitude)
        self.assertIsNone(store.longitude)


class UserModelTest(BaseTestCase):
    """Test User model functionality"""
    
    def test_user_creation(self):
        """Test basic user creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            company=self.company,
            brand=self.brand,
            store=self.store,
            role='cashier',
            role_scope='store',
            pin='1234'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.company, self.company)
        self.assertEqual(user.brand, self.brand)
        self.assertEqual(user.store, self.store)
        self.assertEqual(user.role, 'cashier')
        self.assertEqual(user.role_scope, 'store')
        self.assertEqual(user.pin, '1234')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            company=self.company,
            role='cashier',
            role_scope='store'
        )
        self.assertEqual(str(user), 'testuser (cashier)')
    
    def test_user_can_approve_for_brand(self):
        """Test user brand approval permission"""
        # Manager can approve for their brand
        manager = User.objects.create_user(
            username='manager',
            password='testpass123',
            company=self.company,
            brand=self.brand,
            role='manager',
            role_scope='brand'
        )
        self.assertTrue(manager.can_approve_for_brand(self.brand))
        
        # Admin can approve for any brand in their company
        admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            company=self.company,
            role='admin',
            role_scope='company'
        )
        self.assertTrue(admin.can_approve_for_brand(self.brand))
        
        # Cashier cannot approve
        cashier = User.objects.create_user(
            username='cashier',
            password='testpass123',
            company=self.company,
            brand=self.brand,
            store=self.store,
            role='cashier',
            role_scope='store'
        )
        self.assertFalse(cashier.can_approve_for_brand(self.brand))
    
    def test_user_can_approve_for_store(self):
        """Test user store approval permission"""
        # Supervisor can approve for their store
        supervisor = User.objects.create_user(
            username='supervisor',
            password='testpass123',
            company=self.company,
            brand=self.brand,
            store=self.store,
            role='supervisor',
            role_scope='store'
        )
        self.assertTrue(supervisor.can_approve_for_store(self.store))
        
        # Manager can approve for stores in their brand
        manager = User.objects.create_user(
            username='manager',
            password='testpass123',
            company=self.company,
            brand=self.brand,
            role='manager',
            role_scope='brand'
        )
        self.assertTrue(manager.can_approve_for_store(self.store))
    
    def test_user_defaults(self):
        """Test user default values"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            company=self.company
        )
        
        self.assertEqual(user.role, 'cashier')
        self.assertEqual(user.role_scope, 'store')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


@pytest.mark.unit
class CompanyModelPyTest:
    """Pytest version of Company model tests"""
    
    def test_company_creation(self, company):
        """Test company creation with fixture"""
        assert company.code == 'TEST'
        assert company.name == 'Test Company'
        assert company.is_active is True
    
    def test_company_point_expiry(self, company):
        """Test point expiry configuration"""
        assert company.get_point_expiry_months() == 12


@pytest.mark.unit
class BrandModelPyTest:
    """Pytest version of Brand model tests"""
    
    def test_brand_creation(self, brand):
        """Test brand creation with fixture"""
        assert brand.code == 'TEST-001'
        assert brand.name == 'Test Brand'
        assert brand.is_active is True
    
    def test_brand_company_relationship(self, brand, company):
        """Test brand-company relationship"""
        assert brand.company == company


@pytest.mark.unit
class StoreModelPyTest:
    """Pytest version of Store model tests"""
    
    def test_store_creation(self, store):
        """Test store creation with fixture"""
        assert store.code == 'TEST-001-001'
        assert store.name == 'Test Store BSD'
        assert store.is_active is True
    
    def test_store_brand_relationship(self, store, brand):
        """Test store-brand relationship"""
        assert store.brand == brand


@pytest.mark.unit
class UserModelPyTest:
    """Pytest version of User model tests"""
    
    def test_admin_user_creation(self, admin_user):
        """Test admin user creation with fixture"""
        assert admin_user.username == 'admin'
        assert admin_user.role == 'admin'
        assert admin_user.role_scope == 'company'
        assert admin_user.is_active is True
    
    def test_user_permissions(self, manager_user, brand):
        """Test user permission methods"""
        assert manager_user.can_approve_for_brand(brand) is True
