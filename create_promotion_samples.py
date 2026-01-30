"""
Create Sample Promotions for All Types

This script creates dummy data for all promotion types to help with testing and development.

Usage:
    python manage.py shell < create_promotion_samples.py
    # OR
    python create_promotion_samples.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from promotions.models import Promotion
from core.models import Company, Brand, Store

def get_or_create_test_entities():
    """Get or create test company, brand, and stores"""
    
    # Get first company or create one
    company = Company.objects.first()
    if not company:
        print("❌ No company found. Please create a company first.")
        return None, None, []
    
    # Get first brand or create one
    brand = Brand.objects.filter(company=company).first()
    if not brand:
        print("❌ No brand found. Please create a brand first.")
        return company, None, []
    
    # Get stores
    stores = Store.objects.filter(brand=brand)[:3]
    if not stores:
        print("❌ No stores found. Please create stores first.")
        return company, brand, []
    
    return company, brand, list(stores)


def create_sample_promotions():
    """Create sample promotions for all types"""
    
    print("🚀 Starting promotion sample data creation...")
    print("=" * 60)
    
    # Get entities
    company, brand, stores = get_or_create_test_entities()
    
    if not company or not brand or not stores:
        print("\n❌ Cannot create promotions without company, brand, and stores.")
        print("Please run: python manage.py shell < create_kitchen_sample_data.py")
        return
    
    print(f"✅ Using Company: {company.name}")
    print(f"✅ Using Brand: {brand.name}")
    print(f"✅ Using Stores: {len(stores)} store(s)")
    print("=" * 60)
    
    # Date range
    today = datetime.now().date()
    start_date = today
    end_date = today + timedelta(days=30)
    
    promotions_created = []
    
    # =================================================================
    # 1. PERCENT DISCOUNT - Basic percentage off
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='SAVE20',
        defaults={
            'name': 'Save 20% - Weekend Special',
            'description': 'Get 20% discount on all items during weekend',
            'promo_type': 'percent_discount',
            'discount_percent': Decimal('20.00'),
            'discount_amount': None,
            'max_discount_amount': Decimal('50000.00'),  # Max cap Rp50,000
            'min_purchase': Decimal('100000.00'),  # Min purchase Rp100,000
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': False,
            'is_stackable': True,
            'priority': 100,
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Percent Discount (20% off, max Rp50,000)")
        print(f"   Min Purchase: Rp{promo.min_purchase:,.0f}")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 2. PERCENT DISCOUNT - High discount with cap (Testing >50% warning)
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='MEGA60',
        defaults={
            'name': 'Mega Sale 60% Off',
            'description': 'Massive 60% discount - Limited time only!',
            'promo_type': 'percent_discount',
            'discount_percent': Decimal('60.00'),  # High discount
            'discount_amount': None,
            'max_discount_amount': Decimal('100000.00'),  # Cap at Rp100,000
            'min_purchase': Decimal('200000.00'),  # Min Rp200,000
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': True,  # Member only
            'is_stackable': False,
            'priority': 150,
            'company': company,
            'brand': brand,
            'all_stores': False,
        }
    )
    if created:
        promo.stores.set(stores[:2])  # Apply to first 2 stores only
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Percent Discount (60% off, max Rp100,000) - HIGH DISCOUNT")
        print(f"   Member Only, 2 stores")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 3. AMOUNT DISCOUNT - Fixed amount off
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='FLAT10K',
        defaults={
            'name': 'Flat Rp10,000 Off',
            'description': 'Get instant Rp10,000 discount on your purchase',
            'promo_type': 'amount_discount',
            'discount_percent': None,
            'discount_amount': Decimal('10000.00'),  # Rp10,000 off
            'max_discount_amount': None,
            'min_purchase': Decimal('50000.00'),  # Min Rp50,000
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': True,  # Auto-apply
            'member_only': False,
            'is_stackable': True,
            'priority': 50,
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Amount Discount (Rp10,000 off)")
        print(f"   Auto-apply enabled")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 4. AMOUNT DISCOUNT - Larger amount with higher min purchase
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='CASHBACK50K',
        defaults={
            'name': 'Cashback Rp50,000',
            'description': 'Spend Rp300k and get Rp50k cashback instantly',
            'promo_type': 'amount_discount',
            'discount_percent': None,
            'discount_amount': Decimal('50000.00'),  # Rp50,000 off
            'max_discount_amount': None,
            'min_purchase': Decimal('300000.00'),  # Min Rp300,000
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': False,
            'is_stackable': False,
            'priority': 200,
            'max_uses': 100,  # Limited to 100 uses
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Amount Discount (Rp50,000 off)")
        print(f"   Limited: 100 uses")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 5. HAPPY HOUR - Time-based discount
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='LUNCH30',
        defaults={
            'name': 'Happy Hour Lunch - 30% Off',
            'description': 'Get 30% off during lunch hours (11 AM - 2 PM)',
            'promo_type': 'happy_hour',
            'discount_percent': Decimal('30.00'),
            'discount_amount': None,
            'max_discount_amount': Decimal('30000.00'),  # Max Rp30,000
            'min_purchase': None,
            'valid_time_start': datetime.strptime('11:00', '%H:%M').time(),
            'valid_time_end': datetime.strptime('14:00', '%H:%M').time(),
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': True,
            'member_only': False,
            'is_stackable': False,
            'priority': 120,
            'max_uses_per_day': 50,  # Max 50 uses per day
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Happy Hour (30% off, 11:00-14:00)")
        print(f"   Max 50 uses per day")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 6. HAPPY HOUR - Evening discount
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='DINNER25',
        defaults={
            'name': 'Dinner Special - 25% Off',
            'description': 'Evening discount from 6 PM to 8 PM',
            'promo_type': 'happy_hour',
            'discount_percent': Decimal('25.00'),
            'discount_amount': None,
            'max_discount_amount': Decimal('40000.00'),
            'min_purchase': Decimal('100000.00'),
            'valid_time_start': datetime.strptime('18:00', '%H:%M').time(),
            'valid_time_end': datetime.strptime('20:00', '%H:%M').time(),
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': True,
            'is_stackable': False,
            'priority': 110,
            'company': company,
            'brand': brand,
            'all_stores': False,
        }
    )
    if created:
        promo.stores.set(stores)
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Happy Hour (25% off, 18:00-20:00)")
        print(f"   Member only")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 7. BUY X GET Y (BOGO) - Buy 2 Get 1
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='BOGO21',
        defaults={
            'name': 'Buy 2 Get 1 Free',
            'description': 'Purchase 2 items and get 1 free - Perfect for sharing!',
            'promo_type': 'buy_x_get_y',
            'discount_percent': None,
            'discount_amount': None,
            'buy_quantity': 2,
            'get_quantity': 1,
            'max_discount_amount': None,
            'min_purchase': None,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': False,
            'is_stackable': False,
            'priority': 80,
            'max_uses_per_customer': 3,  # Each customer can use 3 times
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: BOGO (Buy 2 Get 1)")
        print(f"   Max 3 uses per customer")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 8. BUY X GET Y (BOGO) - Buy 3 Get 2
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='BOGO32',
        defaults={
            'name': 'Buy 3 Get 2 Free - Group Deal',
            'description': 'Buy 3 items and get 2 free - Best for groups!',
            'promo_type': 'buy_x_get_y',
            'discount_percent': None,
            'discount_amount': None,
            'buy_quantity': 3,
            'get_quantity': 2,
            'max_discount_amount': None,
            'min_purchase': None,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': True,
            'is_stackable': False,
            'priority': 90,
            'max_uses': 50,  # Limited to 50 total uses
            'company': company,
            'brand': brand,
            'all_stores': False,
        }
    )
    if created:
        promo.stores.set(stores[:1])  # Only first store
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: BOGO (Buy 3 Get 2)")
        print(f"   Member only, limited 50 uses, 1 store")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 9. THRESHOLD TIER - Spend more, save more
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='TIER100K',
        defaults={
            'name': 'Tiered Discount - Spend & Save',
            'description': 'Spend Rp500k get Rp100k off, Spend Rp300k get Rp50k off',
            'promo_type': 'threshold_tier',
            'discount_percent': None,
            'discount_amount': Decimal('100000.00'),  # Rp100k for highest tier
            'max_discount_amount': None,
            'min_purchase': Decimal('500000.00'),  # Minimum Rp500k for this tier
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': True,
            'member_only': False,
            'is_stackable': False,
            'priority': 70,
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Tiered Discount (Rp100k off for Rp500k purchase)")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # 10. PACKAGE DEAL - Bundle pricing (placeholder)
    # =================================================================
    promo, created = Promotion.objects.update_or_create(
        code='PACKAGE1',
        defaults={
            'name': 'Family Package Deal',
            'description': 'Special bundle price for family meal package',
            'promo_type': 'package',
            'discount_percent': None,
            'discount_amount': Decimal('25000.00'),  # Rp25k off package
            'max_discount_amount': None,
            'min_purchase': None,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True,
            'is_auto_apply': False,
            'member_only': False,
            'is_stackable': False,
            'priority': 60,
            'company': company,
            'brand': brand,
            'all_stores': True,
        }
    )
    if created:
        promotions_created.append(promo)
        print(f"✅ Created: {promo.name} ({promo.code})")
        print(f"   Type: Package Deal (Rp25k off)")
    else:
        print(f"ℹ️  Updated: {promo.name} ({promo.code})")
    
    # =================================================================
    # Summary
    # =================================================================
    print("=" * 60)
    print(f"\n🎉 Promotion sample data creation complete!")
    print(f"✅ Total promotions created: {len(promotions_created)}")
    print(f"✅ Total promotions in system: {Promotion.objects.count()}")
    
    print("\n📊 Promotion Types Created:")
    for promo_type, label in Promotion.PROMO_TYPE_CHOICES:
        count = Promotion.objects.filter(promo_type=promo_type).count()
        print(f"   - {label}: {count}")
    
    print("\n🔗 Access promotions at:")
    print("   http://localhost:8002/promotions/")
    
    print("\n📋 Sample Promotion Codes:")
    for promo in Promotion.objects.all().order_by('promo_type', 'code'):
        active_status = "✓" if promo.is_active else "✗"
        print(f"   [{active_status}] {promo.code:15s} - {promo.get_promo_type_display()} - {promo.name}")


if __name__ == '__main__':
    create_sample_promotions()
