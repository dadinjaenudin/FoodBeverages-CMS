"""
Management command to test promotion compiler with real data

Usage:
    python manage.py test_compiler
    python manage.py test_compiler --promotion-id <uuid>
    python manage.py test_compiler --store-id <uuid>
"""

from django.core.management.base import BaseCommand
from promotions.models import Promotion
from promotions.services.compiler import PromotionCompiler
import json


class Command(BaseCommand):
    help = 'Test promotion compiler with real database data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--promotion-id',
            type=str,
            help='Compile specific promotion by ID',
        )
        parser.add_argument(
            '--store-id',
            type=str,
            help='Compile all promotions for specific store',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Compile all active promotions',
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='Pretty print JSON output',
        )

    def handle(self, *args, **options):
        compiler = PromotionCompiler()
        
        self.stdout.write(self.style.SUCCESS('=== Promotion Compiler Test ===\n'))
        
        # Test specific promotion
        if options['promotion_id']:
            self.test_single_promotion(compiler, options['promotion_id'], options['pretty'])
        
        # Test for store
        elif options['store_id']:
            self.test_store_promotions(compiler, options['store_id'], options['pretty'])
        
        # Test all promotions
        elif options['all']:
            self.test_all_promotions(compiler, options['pretty'])
        
        # Default: show stats
        else:
            self.show_stats()
    
    def test_single_promotion(self, compiler, promotion_id, pretty=False):
        """Test compiling a single promotion"""
        try:
            promotion = Promotion.objects.get(id=promotion_id)
            self.stdout.write(f'Testing promotion: {promotion.code} - {promotion.name}\n')
            
            result = compiler.compile_promotion(promotion)
            
            if pretty:
                output = json.dumps(result, indent=2, default=str)
            else:
                output = json.dumps(result, default=str)
            
            self.stdout.write(self.style.SUCCESS('✅ Compilation successful!\n'))
            self.stdout.write(output)
            self.stdout.write('\n')
            
        except Promotion.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Promotion {promotion_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
    
    def test_store_promotions(self, compiler, store_id, pretty=False):
        """Test compiling all promotions for a store"""
        try:
            self.stdout.write(f'Compiling promotions for store: {store_id}\n')
            
            results = compiler.compile_for_store(store_id)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Compiled {len(results)} promotions\n'))
            
            if pretty:
                output = json.dumps(results, indent=2, default=str)
            else:
                output = json.dumps(results, default=str)
            
            self.stdout.write(output)
            self.stdout.write('\n')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
    
    def test_all_promotions(self, compiler, pretty=False):
        """Test compiling all active promotions"""
        promotions = Promotion.objects.filter(is_active=True)
        
        self.stdout.write(f'Found {promotions.count()} active promotions\n')
        
        success = 0
        failed = 0
        
        for promo in promotions:
            try:
                result = compiler.compile_promotion(promo)
                self.stdout.write(self.style.SUCCESS(f'✅ {promo.code}'))
                success += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ {promo.code}: {str(e)}'))
                failed += 1
        
        self.stdout.write(f'\n\nResults:')
        self.stdout.write(self.style.SUCCESS(f'  Success: {success}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'  Failed: {failed}'))
    
    def show_stats(self):
        """Show promotion statistics"""
        total = Promotion.objects.count()
        active = Promotion.objects.filter(is_active=True).count()
        
        self.stdout.write('Promotion Statistics:\n')
        self.stdout.write(f'  Total promotions: {total}')
        self.stdout.write(f'  Active promotions: {active}')
        self.stdout.write(f'  Inactive promotions: {total - active}\n')
        
        # Count by type
        self.stdout.write('\nBy Type:')
        for choice in Promotion.PROMO_TYPE_CHOICES:
            count = Promotion.objects.filter(promo_type=choice[0]).count()
            if count > 0:
                self.stdout.write(f'  {choice[1]}: {count}')
        
        self.stdout.write('\n')
        self.stdout.write('Usage:')
        self.stdout.write('  python manage.py test_compiler --all')
        self.stdout.write('  python manage.py test_compiler --promotion-id <uuid>')
        self.stdout.write('  python manage.py test_compiler --store-id <uuid>')
