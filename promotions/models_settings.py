"""
Promotion Sync Settings Model
Stores configuration for Edge Server synchronization
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Company


class PromotionSyncSettings(models.Model):
    """
    Sync configuration for each company
    Controls what promotions are downloaded by Edge Servers
    """
    
    company = models.OneToOneField(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='promotion_sync_settings',
        primary_key=True
    )
    
    # Date Range Settings
    future_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(0), MaxValueValidator(90)],
        help_text='Download promotions starting within X days in the future (0-90 days)'
    )
    
    past_days = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text='Include promotions that ended X days ago (grace period: 0-30 days)'
    )
    
    # Filtering Options
    SYNC_STRATEGY_CHOICES = [
        ('current_only', 'Current Valid Only - Promotions valid today'),
        ('include_future', 'Include Future - Valid today + future promotions'),
        ('all_active', 'All Active - All active promotions regardless of dates'),
    ]
    
    sync_strategy = models.CharField(
        max_length=20,
        choices=SYNC_STRATEGY_CHOICES,
        default='include_future',
        help_text='Strategy for which promotions to sync to Edge Servers'
    )
    
    include_inactive = models.BooleanField(
        default=False,
        help_text='Include inactive promotions (not recommended)'
    )
    
    # Auto-Sync Settings
    auto_sync_enabled = models.BooleanField(
        default=True,
        help_text='Enable automatic periodic sync'
    )
    
    sync_interval_hours = models.IntegerField(
        default=6,
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text='Sync interval in hours (1-24)'
    )
    
    # Advanced Options
    max_promotions_per_sync = models.IntegerField(
        default=100,
        validators=[MinValueValidator(10), MaxValueValidator(500)],
        help_text='Maximum number of promotions per sync request'
    )
    
    enable_compression = models.BooleanField(
        default=True,
        help_text='Enable gzip compression for API responses'
    )
    
    # Audit
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotion_sync_settings_updates'
    )
    
    class Meta:
        db_table = 'promotion_sync_settings'
        verbose_name = 'Promotion Sync Settings'
        verbose_name_plural = 'Promotion Sync Settings'
    
    def __str__(self):
        return f"Sync Settings - {self.company.name}"
    
    @classmethod
    def get_for_company(cls, company):
        """Get or create settings for a company"""
        settings, created = cls.objects.get_or_create(
            company=company,
            defaults={
                'sync_strategy': 'include_future',
                'future_days': 7,
                'past_days': 1,
            }
        )
        return settings
    
    def get_strategy_display_full(self):
        """Get full description of current strategy"""
        descriptions = {
            'current_only': f'Download only promotions valid today',
            'include_future': f'Download promotions valid today + next {self.future_days} days',
            'all_active': 'Download all active promotions (no date filtering)',
        }
        return descriptions.get(self.sync_strategy, 'Unknown strategy')
