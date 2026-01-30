"""
Management Command: Generate Sample Data for Testing
Creates complete multi-tenant sample data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import uuid


class Command(BaseCommand):
    help = 'Generate sample multi-tenant data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating (DANGEROUS!)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('Generating sample data...'))
        
        # Import models
        from core.models import Company, Brand, Store, User
        from products.models import Category, Product, Modifier, ModifierOption
        from members.models import Member
        
        # Create Company
        company = Company.objects.create(
            code='YGY',
            name='Yogya Group',
            is_active=True,
            point_expiry_months=12,
            points_per_currency=Decimal('1.00')
        )
        self.stdout.write(f'✅ Company: {company.name}')
        
        # Create Brand 1: Ayam Geprek Express
        brand1 = Brand.objects.create(
            company=company,
            code='YGY-001',
            name='Ayam Geprek Express',
            address='Jakarta',
            phone='+62-21-1111111',
            tax_id='01.234.567.8-901.001',
            tax_rate=Decimal('11.00'),
            service_charge=Decimal('5.00'),
            is_active=True
        )
        self.stdout.write(f'✅ Brand: {brand1.name}')
        
        # Create Stores
        store1 = Store.objects.create(
            brand=brand1,
            store_code='YGY-001-BSD',
            store_name='Cabang BSD',
            address='BSD City, Tangerang',
            phone='+62-21-22222',
            timezone='Asia/Jakarta',
            is_active=True
        )
        self.stdout.write(f'✅ Store: {store1.store_name}')
        
        store2 = Store.objects.create(
            brand=brand1,
            store_code='YGY-001-SNY',
            store_name='Cabang Senayan',
            address='Senayan, Jakarta',
            phone='+62-21-33333',
            timezone='Asia/Jakarta',
            is_active=True
        )
        self.stdout.write(f'✅ Store: {store2.store_name}')
        
        # Create Users
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@yogyagroup.com',
            password='admin123',
            company_id=company.id,
            role='ADMIN',
            role_scope='company',
            is_staff=True,
            is_superuser=True
        )
        self.stdout.write(f'✅ User: {admin_user.username} (Admin)')
        
        manager_user = User.objects.create_user(
            username='manager_bsd',
            email='manager@bsd.yogya.com',
            password='manager123',
            company_id=company.id,
            brand_id=brand1.id,
            role='MANAGER',
            role_scope='brand'
        )
        self.stdout.write(f'✅ User: {manager_user.username} (Manager)')
        
        cashier_user = User.objects.create_user(
            username='cashier1',
            email='cashier1@bsd.yogya.com',
            password='cashier123',
            company_id=company.id,
            brand_id=brand1.id,
            role='CASHIER',
            role_scope='store',
            pin='1234'
        )
        self.stdout.write(f'✅ User: {cashier_user.username} (Cashier)')
        
        # Create Categories
        cat_main = Category.objects.create(
            brand=brand1,
            name='Main Course',
            sort_order=1,
            is_active=True
        )
        
        cat_drinks = Category.objects.create(
            brand=brand1,
            name='Drinks',
            sort_order=2,
            is_active=True
        )
        self.stdout.write('✅ Categories created')
        
        # Create Products
        product1 = Product.objects.create(
            brand=brand1,
            category=cat_main,
            sku='GP-001',
            name='Ayam Geprek Original',
            description='Spicy fried chicken with sambal',
            price=Decimal('25000'),
            cost=Decimal('12000'),
            track_stock=False,
            is_active=True,
            sort_order=1
        )
        
        product2 = Product.objects.create(
            brand=brand1,
            category=cat_main,
            sku='GP-002',
            name='Ayam Geprek Keju',
            description='Spicy fried chicken with cheese',
            price=Decimal('30000'),
            cost=Decimal('15000'),
            track_stock=False,
            is_active=True,
            sort_order=2
        )
        
        product3 = Product.objects.create(
            brand=brand1,
            category=cat_drinks,
            sku='DRK-001',
            name='Es Teh Manis',
            price=Decimal('5000'),
            cost=Decimal('2000'),
            track_stock=False,
            is_active=True,
            sort_order=1
        )
        self.stdout.write('✅ Products created')
        
        # Create Modifier
        modifier_level = Modifier.objects.create(
            brand=brand1,
            name='Spicy Level',
            is_required=True,
            max_selections=1,
            is_active=True
        )
        
        ModifierOption.objects.create(
            modifier=modifier_level,
            name='Mild',
            price_adjustment=Decimal('0'),
            is_default=True,
            sort_order=1
        )
        
        ModifierOption.objects.create(
            modifier=modifier_level,
            name='Medium',
            price_adjustment=Decimal('0'),
            sort_order=2
        )
        
        ModifierOption.objects.create(
            modifier=modifier_level,
            name='Extra Hot',
            price_adjustment=Decimal('2000'),
            sort_order=3
        )
        
        product1.modifiers.add(modifier_level)
        product2.modifiers.add(modifier_level)
        self.stdout.write('✅ Modifiers created')
        
        # Create Sample Members
        for i in range(1, 6):
            Member.objects.create(
                company_id=company.id,
                member_code=f'MB-YGY-202601-{i:04d}',
                card_number=f'9999{i:08d}',
                name=f'Member Test {i}',
                phone=f'08123456{i:04d}',
                tier='SILVER' if i % 2 == 0 else 'BRONZE',
                joined_date=timezone.now().date(),
                points=Decimal(i * 100),
                point_balance=Decimal(i * 100),
                total_visits=i * 5,
                total_spent=Decimal(i * 50000),
                is_active=True
            )
        self.stdout.write('✅ Sample members created')
        
        # Generate table areas and tables
        self.generate_table_areas()
        
        self.stdout.write(self.style.SUCCESS('\n✨ Sample data generation complete!'))
        self.stdout.write(self.style.SUCCESS('\n📋 Login credentials:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Manager: manager_bsd / manager123')
        self.stdout.write('  Cashier: cashier1 / cashier123 (PIN: 1234)')

    def clear_data(self):
        """Clear existing test data (except superuser)"""
        from core.models import Company, Brand, Store, User
        from products.models import Category, Product, Modifier, ModifierOption, ProductModifier
        from members.models import Member, MemberTransaction
        
        # Clear in reverse order due to foreign keys
        MemberTransaction.objects.all().delete()
        Member.objects.all().delete()
        ProductModifier.objects.all().delete()
        ModifierOption.objects.all().delete()
        Modifier.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Store.objects.all().delete()
        Brand.objects.all().delete()
        Company.objects.all().delete()
        
        self.stdout.write(self.style.WARNING('✓ Data cleared'))
    
    def generate_table_areas(self):
        """Generate sample table areas and tables"""
        from products.models import TableArea, Tables
        import random
        
        self.stdout.write('\n🏢 Creating Table Areas and Tables...')
        
        # Get brands
        brands = Brand.objects.filter(is_active=True)
        if not brands.exists():
            self.stdout.write(self.style.WARNING('No brands found, skipping table areas'))
            return
        
        # Table area configurations
        areas_config = [
            {
                'name': 'Indoor Main Hall', 
                'sort_order': 1,
                'tables': [
                    {'number': 'A1', 'capacity': 4, 'pos_x': 100, 'pos_y': 100},
                    {'number': 'A2', 'capacity': 4, 'pos_x': 200, 'pos_y': 100},
                    {'number': 'A3', 'capacity': 6, 'pos_x': 300, 'pos_y': 100},
                    {'number': 'A4', 'capacity': 2, 'pos_x': 100, 'pos_y': 200},
                    {'number': 'A5', 'capacity': 4, 'pos_x': 200, 'pos_y': 200},
                    {'number': 'A6', 'capacity': 8, 'pos_x': 300, 'pos_y': 200},
                ]
            },
            {
                'name': 'Outdoor Terrace', 
                'sort_order': 2,
                'tables': [
                    {'number': 'T1', 'capacity': 4, 'pos_x': 150, 'pos_y': 50},
                    {'number': 'T2', 'capacity': 4, 'pos_x': 250, 'pos_y': 50},
                    {'number': 'T3', 'capacity': 6, 'pos_x': 150, 'pos_y': 150},
                    {'number': 'T4', 'capacity': 2, 'pos_x': 250, 'pos_y': 150},
                ]
            },
            {
                'name': 'VIP Room', 
                'sort_order': 3,
                'tables': [
                    {'number': 'VIP1', 'capacity': 8, 'pos_x': 200, 'pos_y': 100},
                    {'number': 'VIP2', 'capacity': 12, 'pos_x': 200, 'pos_y': 250},
                ]
            },
            {
                'name': 'Private Dining', 
                'sort_order': 4,
                'tables': [
                    {'number': 'PD1', 'capacity': 10, 'pos_x': 150, 'pos_y': 100},
                    {'number': 'PD2', 'capacity': 6, 'pos_x': 250, 'pos_y': 100},
                ]
            },
            {
                'name': 'Bar Area', 
                'sort_order': 5,
                'tables': [
                    {'number': 'B1', 'capacity': 2, 'pos_x': 100, 'pos_y': 50},
                    {'number': 'B2', 'capacity': 2, 'pos_x': 150, 'pos_y': 50},
                    {'number': 'B3', 'capacity': 4, 'pos_x': 200, 'pos_y': 50},
                    {'number': 'B4', 'capacity': 2, 'pos_x': 250, 'pos_y': 50},
                    {'number': 'B5', 'capacity': 2, 'pos_x': 300, 'pos_y': 50},
                ]
            }
        ]
        
        # Create areas and tables for each brand
        total_areas_created = 0
        total_tables_created = 0
        
        for brand in brands:
            for area_config in areas_config:
                # Create or get table area
                area, area_created = TableArea.objects.get_or_create(
                    brand=brand,
                    name=area_config['name'],
                    defaults={
                        'sort_order': area_config['sort_order'],
                        'is_active': True
                    }
                )
                
                if area_created:
                    total_areas_created += 1
                    self.stdout.write(f'  📍 Created area: {area.name} ({brand.name})')
                    
                    # Create tables for this area
                    for table_config in area_config['tables']:
                        # Random status for demo
                        statuses = ['available', 'occupied', 'reserved']
                        weights = [0.6, 0.3, 0.1]  # 60% available, 30% occupied, 10% reserved
                        status = random.choices(statuses, weights=weights)[0]
                        
                        table = Tables.objects.create(
                            area=area,
                            number=table_config['number'],
                            capacity=table_config['capacity'],
                            pos_x=table_config['pos_x'],
                            pos_y=table_config['pos_y'],
                            status=status,
                            is_active=True,
                            qr_code=f"QR-{brand.name.replace(' ', '')}-{area.name.replace(' ', '')}-{table_config['number']}"
                        )
                        total_tables_created += 1
                        status_icon = {'available': '🟢', 'occupied': '🔴', 'reserved': '🟡'}[status]
                        self.stdout.write(f'    🪑 Table {table.number} - {table.capacity} seats {status_icon}')
        
        self.stdout.write(f'✅ Table Areas: {total_areas_created} areas, {total_tables_created} tables created')
