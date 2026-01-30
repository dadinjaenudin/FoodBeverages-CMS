# Generated manually by AI Assistant on 2026-01-26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_add_store_selection'),
        ('core', '0008_add_store_to_tablearea'),  # Assuming latest core migration
    ]

    operations = [
        # Add cross-brand boolean flag
        migrations.AddField(
            model_name='promotion',
            name='is_cross_brand',
            field=models.BooleanField(default=False, help_text='Enable cross-brand promotion rules'),
        ),
        
        # Add cross-brand type
        migrations.AddField(
            model_name='promotion',
            name='cross_brand_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('trigger_benefit', 'Buy from Brand A → Discount at Brand B'),
                    ('multi_brand_spend', 'Spend at Multiple Brands → Get Reward'),
                    ('cross_brand_bundle', 'Cross-Brand Product Bundle'),
                    ('loyalty_accumulate', 'Accumulate Points Across Brands'),
                    ('same_receipt', 'Multiple Brands in Same Transaction'),
                ],
                help_text='Type of cross-brand promotion',
                max_length=50,
                null=True
            ),
        ),
        
        # Add trigger_min_amount
        migrations.AddField(
            model_name='promotion',
            name='trigger_min_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Minimum purchase amount in trigger brands',
                max_digits=10,
                null=True
            ),
        ),
        
        # Add cross_brand_rules JSON field
        migrations.AddField(
            model_name='promotion',
            name='cross_brand_rules',
            field=models.JSONField(
                blank=True,
                help_text='Complex cross-brand rules in JSON format',
                null=True
            ),
        ),
        
        # Add trigger_brands M2M
        migrations.AddField(
            model_name='promotion',
            name='trigger_brands',
            field=models.ManyToManyField(
                blank=True,
                help_text='Brands where purchase triggers the promotion',
                related_name='trigger_promotions',
                to='core.brand'
            ),
        ),
        
        # Add benefit_brands M2M
        migrations.AddField(
            model_name='promotion',
            name='benefit_brands',
            field=models.ManyToManyField(
                blank=True,
                help_text='Brands where customer gets the benefit',
                related_name='benefit_promotions',
                to='core.brand'
            ),
        ),
    ]
