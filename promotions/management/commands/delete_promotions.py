"""
Delete Promotions

Usage:
    # Delete all promotions
    python manage.py delete_promotions --all
    
    # Delete by code
    python manage.py delete_promotions --code SAVE20
    
    # Delete by type
    python manage.py delete_promotions --type percent_discount
    
    # Delete inactive promotions
    python manage.py delete_promotions --inactive
    
    # Delete expired promotions
    python manage.py delete_promotions --expired
    
    # Delete sample promotions (created by script)
    python manage.py delete_promotions --samples
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from promotions.models import Promotion


class Command(BaseCommand):
    help = 'Delete promotions based on various criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete ALL promotions (use with caution!)',
        )
        parser.add_argument(
            '--code',
            type=str,
            help='Delete promotion by code (e.g., SAVE20)',
        )
        parser.add_argument(
            '--type',
            type=str,
            help='Delete promotions by type (e.g., percent_discount)',
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Delete inactive promotions only',
        )
        parser.add_argument(
            '--expired',
            action='store_true',
            help='Delete expired promotions only',
        )
        parser.add_argument(
            '--samples',
            action='store_true',
            help='Delete sample promotions created by script',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🗑️  Promotion Deletion Tool'))
        self.stdout.write('=' * 60)
        
        # Determine what to delete
        promotions = None
        description = ""
        
        if options['all']:
            promotions = Promotion.objects.all()
            description = "ALL promotions"
        
        elif options['code']:
            promotions = Promotion.objects.filter(code=options['code'])
            description = f"promotion with code '{options['code']}'"
        
        elif options['type']:
            promotions = Promotion.objects.filter(promo_type=options['type'])
            description = f"promotions of type '{options['type']}'"
        
        elif options['inactive']:
            promotions = Promotion.objects.filter(is_active=False)
            description = "inactive promotions"
        
        elif options['expired']:
            today = timezone.now().date()
            promotions = Promotion.objects.filter(end_date__lt=today)
            description = "expired promotions"
        
        elif options['samples']:
            # Sample promotion codes created by script
            sample_codes = [
                'SAVE20', 'MEGA60', 'FLAT10K', 'CASHBACK50K',
                'LUNCH30', 'DINNER25', 'BOGO21', 'BOGO32',
                'TIER100K', 'PACKAGE1', 'EXTRA10', 'SUPER50',
                'AFTERNOON20', 'BOGO31', 'WEEKEND15'
            ]
            promotions = Promotion.objects.filter(code__in=sample_codes)
            description = "sample promotions"
        
        else:
            self.stdout.write(self.style.ERROR('❌ No deletion criteria specified!'))
            self.stdout.write('\nPlease specify one of:')
            self.stdout.write('  --all          Delete all promotions')
            self.stdout.write('  --code CODE    Delete by code')
            self.stdout.write('  --type TYPE    Delete by type')
            self.stdout.write('  --inactive     Delete inactive')
            self.stdout.write('  --expired      Delete expired')
            self.stdout.write('  --samples      Delete sample data')
            return
        
        # Check if any found
        count = promotions.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING(f'\n⚠️  No {description} found.'))
            return
        
        # Display what will be deleted
        self.stdout.write(f'\n📋 Found {count} {description}:')
        self.stdout.write('-' * 60)
        
        for promo in promotions[:20]:  # Show first 20
            status = "✓" if promo.is_active else "✗"
            self.stdout.write(
                f'  [{status}] {promo.code:15s} - {promo.get_promo_type_display():20s} - {promo.name}'
            )
        
        if count > 20:
            self.stdout.write(f'  ... and {count - 20} more')
        
        # Confirmation
        if not options['confirm']:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.ERROR(f'⚠️  WARNING: This will DELETE {count} promotion(s)!'))
            self.stdout.write(self.style.ERROR('This action CANNOT be undone!'))
            self.stdout.write('=' * 60)
            
            confirm = input('\nType "DELETE" to confirm: ')
            
            if confirm != 'DELETE':
                self.stdout.write(self.style.WARNING('\n❌ Deletion cancelled.'))
                return
        
        # Delete
        self.stdout.write('\n🗑️  Deleting promotions...')
        
        deleted_count = 0
        for promo in promotions:
            code = promo.code
            name = promo.name
            promo.delete()
            deleted_count += 1
            self.stdout.write(f'  ✓ Deleted: {code} - {name}')
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully deleted {deleted_count} promotion(s)!'))
        self.stdout.write(f'📊 Remaining promotions: {Promotion.objects.count()}')
