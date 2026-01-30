# Generated manually for PromotionSyncSettings model

from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_store_to_tablearea'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('promotions', '0003_add_cross_brand_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionSyncSettings',
            fields=[
                ('company', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='promotion_sync_settings',
                    serialize=False,
                    to='core.company'
                )),
                ('future_days', models.IntegerField(
                    default=7,
                    help_text='Download promotions starting within X days in the future (0-90 days)',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(90)
                    ]
                )),
                ('past_days', models.IntegerField(
                    default=1,
                    help_text='Include promotions that ended X days ago (grace period: 0-30 days)',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(30)
                    ]
                )),
                ('sync_strategy', models.CharField(
                    choices=[
                        ('current_only', 'Current Valid Only - Promotions valid today'),
                        ('include_future', 'Include Future - Valid today + future promotions'),
                        ('all_active', 'All Active - All active promotions regardless of dates')
                    ],
                    default='include_future',
                    help_text='Strategy for which promotions to sync to Edge Servers',
                    max_length=20
                )),
                ('include_inactive', models.BooleanField(
                    default=False,
                    help_text='Include inactive promotions (not recommended)'
                )),
                ('auto_sync_enabled', models.BooleanField(
                    default=True,
                    help_text='Enable automatic periodic sync'
                )),
                ('sync_interval_hours', models.IntegerField(
                    default=6,
                    help_text='Sync interval in hours (1-24)',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(24)
                    ]
                )),
                ('max_promotions_per_sync', models.IntegerField(
                    default=100,
                    help_text='Maximum number of promotions per sync request',
                    validators=[
                        django.core.validators.MinValueValidator(10),
                        django.core.validators.MaxValueValidator(500)
                    ]
                )),
                ('enable_compression', models.BooleanField(
                    default=True,
                    help_text='Enable gzip compression for API responses'
                )),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='promotion_sync_settings_updates',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Promotion Sync Settings',
                'verbose_name_plural': 'Promotion Sync Settings',
                'db_table': 'promotion_sync_settings',
            },
        ),
    ]
