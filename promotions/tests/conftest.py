"""
Pytest configuration for promotions app
Provides fixtures for testing
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
from promotions.models import Promotion, PromotionTier, PackagePromotion, PackageItem
from core.models import Company, Brand, Store, User
from products.models import Category, Product


@pytest.fixture
def sample_company(db):
    """Create sample company"""
    return Company.objects.create(
        name="Test Company",
        code="TEST-CO"
    )


@pytest.fixture
def sample_brand(db, sample_company):
    """Create sample brand"""
    return Brand.objects.create(
        company=sample_company,
        name="Test Brand",
        code="TEST-BRAND"
    )


@pytest.fixture
def sample_store(db, sample_company, sample_brand):
    """Create sample store"""
    return Store.objects.create(
        company=sample_company,
        brand=sample_brand,
        name="Test Store",
        code="TEST-STORE",
        address="Test Address"
    )


@pytest.fixture
def sample_user(db, sample_company):
    """Create sample user"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        company=sample_company,
        role_scope="company"
    )


@pytest.fixture
def sample_category(db, sample_company):
    """Create sample category"""
    return Category.objects.create(
        company=sample_company,
        name="Test Category",
        code="TEST-CAT"
    )


@pytest.fixture
def sample_product(db, sample_company, sample_brand, sample_category):
    """Create sample product"""
    return Product.objects.create(
        company=sample_company,
        brand=sample_brand,
        category=sample_category,
        name="Test Product",
        sku="TEST-SKU",
        price=Decimal('50000.00')
    )


@pytest.fixture
def base_promotion_data(sample_company, sample_user):
    """Base data for creating promotions"""
    today = timezone.now().date()
    return {
        'company': sample_company,
        'name': 'Test Promotion',
        'code': 'TEST-PROMO',
        'start_date': today,
        'end_date': today + timedelta(days=30),
        'created_by': sample_user,
        'is_active': True,
    }


@pytest.fixture
def percent_discount_promotion(db, base_promotion_data):
    """Create percent discount promotion"""
    return Promotion.objects.create(
        **base_promotion_data,
        promo_type='percent_discount',
        discount_percent=Decimal('20.00'),
        max_discount_amount=Decimal('50000.00'),
        min_purchase=Decimal('100000.00')
    )


@pytest.fixture
def amount_discount_promotion(db, base_promotion_data):
    """Create amount discount promotion"""
    return Promotion.objects.create(
        **base_promotion_data,
        code='AMOUNT-TEST',
        promo_type='amount_discount',
        discount_amount=Decimal('10000.00'),
        min_purchase=Decimal('50000.00')
    )


@pytest.fixture
def bogo_promotion(db, base_promotion_data):
    """Create BOGO promotion"""
    return Promotion.objects.create(
        **base_promotion_data,
        code='BOGO-TEST',
        promo_type='buy_x_get_y',
        buy_quantity=2,
        get_quantity=1,
        discount_percent=Decimal('100.00')
    )


@pytest.fixture
def combo_promotion(db, base_promotion_data, sample_product):
    """Create combo promotion"""
    promo = Promotion.objects.create(
        **base_promotion_data,
        code='COMBO-TEST',
        promo_type='combo',
        combo_price=Decimal('45000.00')
    )
    promo.combo_products.add(sample_product)
    return promo


@pytest.fixture
def happy_hour_promotion(db, base_promotion_data):
    """Create happy hour promotion"""
    from datetime import time
    return Promotion.objects.create(
        **base_promotion_data,
        code='HAPPY-TEST',
        promo_type='happy_hour',
        discount_percent=Decimal('50.00'),
        valid_time_start=time(14, 0),
        valid_time_end=time(17, 0),
        valid_days=[1, 2, 3, 4, 5]
    )
