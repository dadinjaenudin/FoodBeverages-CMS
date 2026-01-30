"""
Comprehensive Test Suite for Promotion Sync API
Tests all Edge Server sync endpoints
"""

import pytest
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal

from core.models import Company, Brand, Store, User
from promotions.models import Promotion
from promotions.models_settings import PromotionSyncSettings
from products.models import Category, Product


@pytest.mark.django_db
class TestSyncPromotionsAPI:
    """Test /api/v1/sync/promotions/ endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        # Create company
        self.company = Company.objects.create(
            code='TEST',
            name='Test Company',
            timezone='Asia/Jakarta'
        )
        
        # Create brand
        self.brand = Brand.objects.create(
            company=self.company,
            code='TEST-BR1',
            name='Test Brand'
        )
        
        # Create store
        self.store = Store.objects.create(
            brand=self.brand,
            store_code='TEST-ST1',
            store_name='Test Store',
            address='Test Address',
            phone='123456789'
        )
        
        # Create user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            company=self.company,
            brand=self.brand,
            store=self.store
        )
        
        # Create sync settings
        self.sync_settings = PromotionSyncSettings.objects.create(
            company=self.company,
            sync_strategy='include_future',
            future_days=7,
            past_days=1,
            max_promotions_per_sync=100
        )
        
        # Create test promotions
        self.promotion_current = Promotion.objects.create(
            company=self.company,
            brand=self.brand,
            name='Current Promotion',
            discount_type='percent',
            discount_value=Decimal('10.00'),
            start_date=timezone.now().date() - timedelta(days=1),
            end_date=timezone.now().date() + timedelta(days=5),
            is_active=True,
            all_stores=True
        )
        
        self.promotion_future = Promotion.objects.create(
            company=self.company,
            brand=self.brand,
            name='Future Promotion',
            discount_type='amount',
            discount_value=Decimal('5000.00'),
            start_date=timezone.now().date() + timedelta(days=3),
            end_date=timezone.now().date() + timedelta(days=10),
            is_active=True,
            all_stores=True
        )
        
        self.promotion_expired = Promotion.objects.create(
            company=self.company,
            brand=self.brand,
            name='Expired Promotion',
            discount_type='percent',
            discount_value=Decimal('20.00'),
            start_date=timezone.now().date() - timedelta(days=10),
            end_date=timezone.now().date() - timedelta(days=5),
            is_active=True,
            all_stores=True
        )
        
        self.promotion_inactive = Promotion.objects.create(
            company=self.company,
            brand=self.brand,
            name='Inactive Promotion',
            discount_type='percent',
            discount_value=Decimal('15.00'),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=5),
            is_active=False,
            all_stores=True
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_sync_promotions_success(self):
        """Test successful promotion sync"""
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'promotions' in data
        assert 'sync_timestamp' in data
        assert 'total' in data
        assert 'settings' in data
        assert 'store' in data
        
        # Should include current and future, exclude expired
        assert data['total'] >= 2
        
    def test_sync_promotions_missing_store_id(self):
        """Test error when store_id is missing"""
        response = self.client.get('/api/v1/sync/promotions/', {
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['code'] == 'MISSING_STORE_ID'
    
    def test_sync_promotions_missing_company_id(self):
        """Test error when company_id is missing"""
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id)
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['code'] == 'MISSING_COMPANY_ID'
    
    def test_sync_promotions_invalid_store(self):
        """Test error with invalid store_id"""
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': '00000000-0000-0000-0000-000000000000',
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['code'] == 'STORE_NOT_FOUND'
    
    def test_sync_promotions_strategy_current_only(self):
        """Test sync with current_only strategy"""
        self.sync_settings.sync_strategy = 'current_only'
        self.sync_settings.save()
        
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only include current promotion
        promotion_names = [p['name'] for p in data['promotions']]
        assert 'Current Promotion' in promotion_names
        assert 'Future Promotion' not in promotion_names
    
    def test_sync_promotions_strategy_include_future(self):
        """Test sync with include_future strategy"""
        self.sync_settings.sync_strategy = 'include_future'
        self.sync_settings.save()
        
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should include current and future
        promotion_names = [p['name'] for p in data['promotions']]
        assert 'Current Promotion' in promotion_names
        assert 'Future Promotion' in promotion_names
    
    def test_sync_promotions_strategy_all_active(self):
        """Test sync with all_active strategy"""
        self.sync_settings.sync_strategy = 'all_active'
        self.sync_settings.save()
        
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should include all active promotions (including expired)
        promotion_names = [p['name'] for p in data['promotions']]
        assert 'Current Promotion' in promotion_names
        assert 'Future Promotion' in promotion_names
        assert 'Expired Promotion' in promotion_names
    
    def test_sync_promotions_include_inactive(self):
        """Test sync with include_inactive setting"""
        self.sync_settings.include_inactive = True
        self.sync_settings.save()
        
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should include inactive promotion
        promotion_names = [p['name'] for p in data['promotions']]
        assert 'Inactive Promotion' in promotion_names
    
    def test_sync_promotions_incremental_sync(self):
        """Test incremental sync with updated_since parameter"""
        # Update one promotion
        self.promotion_current.name = 'Updated Promotion'
        self.promotion_current.save()
        
        # Sync with updated_since before the update
        updated_since = (timezone.now() - timedelta(minutes=1)).isoformat()
        
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id),
            'updated_since': updated_since
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only return updated promotion
        assert data['total'] >= 1
    
    def test_sync_promotions_max_limit(self):
        """Test max_promotions_per_sync limit"""
        # Set low limit
        self.sync_settings.max_promotions_per_sync = 1
        self.sync_settings.save()
        
        response = self.client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should respect the limit
        assert data['total'] <= 1
        assert data['total_available'] >= 2
    
    def test_sync_promotions_authentication_required(self):
        """Test that authentication is required"""
        client = APIClient()  # Unauthenticated client
        
        response = client.get('/api/v1/sync/promotions/', {
            'store_id': str(self.store.id),
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSyncCategoriesAPI:
    """Test /api/v1/sync/categories/ endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.company = Company.objects.create(
            code='TEST',
            name='Test Company'
        )
        
        self.brand = Brand.objects.create(
            company=self.company,
            code='TEST-BR1',
            name='Test Brand'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            company=self.company
        )
        
        # Create categories
        self.category1 = Category.objects.create(
            company=self.company,
            brand=self.brand,
            name='Category 1',
            code='CAT1',
            is_active=True
        )
        
        self.category2 = Category.objects.create(
            company=self.company,
            brand=self.brand,
            name='Category 2',
            code='CAT2',
            is_active=True
        )
        
        self.category_inactive = Category.objects.create(
            company=self.company,
            brand=self.brand,
            name='Inactive Category',
            code='CAT3',
            is_active=False
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_sync_categories_success(self):
        """Test successful category sync"""
        response = self.client.get('/api/v1/sync/categories/', {
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'categories' in data
        assert 'sync_timestamp' in data
        assert 'total' in data
        
        # Should only return active categories
        assert data['total'] == 2
    
    def test_sync_categories_missing_company_id(self):
        """Test error when company_id is missing"""
        response = self.client.get('/api/v1/sync/categories/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['code'] == 'MISSING_COMPANY_ID'
    
    def test_sync_categories_filter_by_brand(self):
        """Test filtering categories by brand"""
        response = self.client.get('/api/v1/sync/categories/', {
            'company_id': str(self.company.id),
            'brand_id': str(self.brand.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All categories should belong to the brand
        for cat in data['categories']:
            assert cat['brand_id'] == str(self.brand.id)


@pytest.mark.django_db
class TestSyncProductsAPI:
    """Test /api/v1/sync/products/ endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.company = Company.objects.create(
            code='TEST',
            name='Test Company'
        )
        
        self.brand = Brand.objects.create(
            company=self.company,
            code='TEST-BR1',
            name='Test Brand'
        )
        
        self.category = Category.objects.create(
            company=self.company,
            brand=self.brand,
            name='Test Category',
            code='CAT1'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            company=self.company
        )
        
        # Create products
        self.product1 = Product.objects.create(
            company=self.company,
            brand=self.brand,
            category=self.category,
            name='Product 1',
            sku='P001',
            price=Decimal('10000.00'),
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            company=self.company,
            brand=self.brand,
            category=self.category,
            name='Product 2',
            sku='P002',
            price=Decimal('15000.00'),
            is_active=True
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_sync_products_success(self):
        """Test successful product sync"""
        response = self.client.get('/api/v1/sync/products/', {
            'company_id': str(self.company.id),
            'brand_id': str(self.brand.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'products' in data
        assert 'sync_timestamp' in data
        assert 'total' in data
        assert data['total'] == 2
    
    def test_sync_products_missing_company_id(self):
        """Test error when company_id is missing"""
        response = self.client.get('/api/v1/sync/products/', {
            'brand_id': str(self.brand.id)
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['code'] == 'MISSING_COMPANY_ID'
    
    def test_sync_products_missing_brand_id(self):
        """Test error when brand_id is missing"""
        response = self.client.get('/api/v1/sync/products/', {
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['code'] == 'MISSING_BRAND_ID'


@pytest.mark.django_db
class TestSyncVersionAPI:
    """Test /api/v1/sync/version/ endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.company = Company.objects.create(
            code='TEST',
            name='Test Company'
        )
        
        self.brand = Brand.objects.create(
            company=self.company,
            code='TEST-BR1',
            name='Test Brand'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            company=self.company
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_sync_version_success(self):
        """Test sync version endpoint"""
        response = self.client.get('/api/v1/sync/version/', {
            'company_id': str(self.company.id)
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'version' in data
        assert 'last_updated' in data
        assert 'force_update' in data
    
    def test_sync_version_missing_company_id(self):
        """Test error when company_id is missing"""
        response = self.client.get('/api/v1/sync/version/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUploadUsageAPI:
    """Test /api/v1/sync/usage/ endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.company = Company.objects.create(
            code='TEST',
            name='Test Company'
        )
        
        self.brand = Brand.objects.create(
            company=self.company,
            code='TEST-BR1',
            name='Test Brand'
        )
        
        self.store = Store.objects.create(
            brand=self.brand,
            store_code='TEST-ST1',
            store_name='Test Store',
            address='Test Address',
            phone='123456789'
        )
        
        self.promotion = Promotion.objects.create(
            company=self.company,
            brand=self.brand,
            name='Test Promotion',
            discount_type='percent',
            discount_value=Decimal('10.00'),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=5),
            is_active=True,
            all_stores=True
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            company=self.company
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_upload_usage_success(self):
        """Test successful usage upload"""
        usage_data = {
            'usages': [
                {
                    'promotion_id': str(self.promotion.id),
                    'bill_id': 'B001',
                    'discount_amount': 15000.0,
                    'used_at': timezone.now().isoformat(),
                    'store_id': str(self.store.id)
                },
                {
                    'promotion_id': str(self.promotion.id),
                    'bill_id': 'B002',
                    'discount_amount': 20000.0,
                    'used_at': timezone.now().isoformat(),
                    'store_id': str(self.store.id)
                }
            ]
        }
        
        response = self.client.post('/api/v1/sync/usage/', 
                                    usage_data, 
                                    format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'created' in data
        assert 'total' in data
        assert data['total'] == 2
    
    def test_upload_usage_empty_array(self):
        """Test error when usages array is empty"""
        response = self.client.post('/api/v1/sync/usage/', 
                                    {'usages': []}, 
                                    format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

