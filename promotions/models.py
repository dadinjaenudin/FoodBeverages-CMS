"""
Promotion Engine Models
Comprehensive F&B promotion system with 12+ types
Based on DATABASE_ERD.md specifications
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import Company, Brand, Store, User
from products.models import Category, Product
from members.models import Member


class Promotion(models.Model):
    """
    Promotion - Comprehensive promotion engine
    Supports 12+ promotion types with complex rules
    """
    PROMO_TYPE_CHOICES = [
        ('percent_discount', 'Percent Discount'),
        ('amount_discount', 'Amount Discount'),
        ('buy_x_get_y', 'Buy X Get Y (BOGO)'),
        ('combo', 'Combo Deal'),
        ('free_item', 'Free Item'),
        ('happy_hour', 'Happy Hour'),
        ('cashback', 'Cashback'),
        ('payment_discount', 'Payment Method Discount'),
        ('package', 'Package/Set Menu'),
        ('mix_match', 'Mix & Match'),
        ('upsell', 'Upsell/Add-on'),
        ('threshold_tier', 'Threshold/Tiered'),
    ]
    
    APPLY_TO_CHOICES = [
        ('all', 'All Products'),
        ('category', 'Specific Categories'),
        ('product', 'Specific Products'),
        ('bill', 'Bill/Subtotal Level'),
        ('payment', 'Payment Method'),
    ]

    CROSS_BRAND_TYPES = [
        ('trigger_benefit', 'Buy from Brand A → Discount at Brand B'),
        ('multi_brand_spend', 'Spend at Multiple Brands → Get Reward'),
        ('cross_brand_bundle', 'Cross-Brand Product Bundle'),
        ('loyalty_accumulate', 'Accumulate Points Across Brands'),
        ('same_receipt', 'Multiple Brands in Same Transaction'),
    ]
    
    SCOPE_CHOICES = [
        ('company', 'Company-wide'),
        ('brands', 'Multiple Brands'),
        ('single', 'Single Brand'),
    ]
    
    CUSTOMER_TYPE_CHOICES = [
        ('all', 'All Customers'),
        ('first_order', 'First Order Ever'),
        ('first_per_brand', 'First Order per Brand'),
        ('comeback', 'Comeback Customer'),
        ('inactive', 'Inactive Customer'),
    ]
    
    EXECUTION_STAGE_CHOICES = [
        ('item_level', 'Item Level - Auto-calculate saat add product'),
        ('cart_level', 'Cart Level - Calculate saat klik button'),
        ('payment_level', 'Payment Level - Calculate saat payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='promotions')
    
    # Basic Info
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    # Promotion Type
    promo_type = models.CharField(max_length=30, choices=PROMO_TYPE_CHOICES)
    apply_to = models.CharField(max_length=20, choices=APPLY_TO_CHOICES, default='all')
    
    # Multi-Brand Scope
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='company')
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='single_brand_promotions',
        null=True,
        blank=True,
        help_text="For single brand scope only"
    )
    brands = models.ManyToManyField(Brand, related_name='multi_brand_promotions', blank=True)
    exclude_brands = models.ManyToManyField(Brand, related_name='excluded_promotions', blank=True)
    
    # Store Selection
    all_stores = models.BooleanField(
        default=True,
        help_text="Apply to all stores in scope (company/brand)"
    )
    stores = models.ManyToManyField(
        Store,
        related_name='promotions',
        blank=True,
        help_text="Specific stores (if all_stores=False)"
    )
    
    # Discount Configuration
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cap discount amount"
    )
    
    # BOGO (Buy X Get Y)
    buy_quantity = models.IntegerField(default=0)
    get_quantity = models.IntegerField(default=0)
    get_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='bogo_promotions',
        null=True,
        blank=True
    )
    
    # Combo
    combo_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    combo_products = models.ManyToManyField(Product, related_name='combo_promotions', blank=True)
    
    # Happy Hour
    happy_hour_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment Method Promo
    payment_methods = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON array: ['cash', 'card', 'qris', 'gopay', 'ovo']"
    )
    payment_min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Product/Category Filters
    categories = models.ManyToManyField(Category, related_name='promotions', blank=True)
    products = models.ManyToManyField(Product, related_name='direct_promotions', blank=True)
    exclude_categories = models.ManyToManyField(Category, related_name='excluded_promotions', blank=True)
    exclude_products = models.ManyToManyField(Product, related_name='excluded_from_promotions', blank=True)
    
    # Cross-Brand Promotion (NEW!)
    is_cross_brand = models.BooleanField(
        default=False,
        help_text="Enable cross-brand promotion rules"
    )
    cross_brand_type = models.CharField(
        max_length=50,
        choices=CROSS_BRAND_TYPES,
        null=True,
        blank=True,
        help_text="Type of cross-brand promotion"
    )
    trigger_brands = models.ManyToManyField(
        'core.Brand',
        related_name='trigger_promotions',
        blank=True,
        help_text="Brands where purchase triggers the promotion"
    )
    trigger_min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum purchase amount in trigger brands"
    )
    benefit_brands = models.ManyToManyField(
        'core.Brand',
        related_name='benefit_promotions',
        blank=True,
        help_text="Brands where customer gets the benefit"
    )
    cross_brand_rules = models.JSONField(
        null=True,
        blank=True,
        help_text="Complex cross-brand rules in JSON format"
    )
    
    # Member Tier
    member_only = models.BooleanField(default=False)
    member_tiers = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON array: ['bronze', 'silver', 'gold', 'platinum']"
    )
    exclude_members = models.ManyToManyField(Member, related_name='excluded_promotions', blank=True)
    
    # Time Rules
    start_date = models.DateField()
    end_date = models.DateField()
    valid_days = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON array: [0-6] (0=Monday, 6=Sunday)"
    )
    valid_time_start = models.TimeField(null=True, blank=True)
    valid_time_end = models.TimeField(null=True, blank=True)
    exclude_holidays = models.BooleanField(default=False)
    
    # Usage Limits
    max_uses = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total max uses (null=unlimited)"
    )
    max_uses_per_customer = models.IntegerField(
        null=True,
        blank=True,
        help_text="Max uses per customer"
    )
    max_uses_per_day = models.IntegerField(null=True, blank=True)
    current_uses = models.IntegerField(default=0, help_text="Updated by Edge")
    
    # Requirements
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_quantity = models.IntegerField(default=0)
    min_items = models.IntegerField(default=0)
    
    # Stacking & Priority
    is_stackable = models.BooleanField(default=False)
    priority = models.IntegerField(default=0, help_text="Higher = execute first")
    cannot_combine_with = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='incompatible_promotions',
        blank=True
    )
    
    # Channel-Based
    sales_channels = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON array: ['dine_in', 'takeaway', 'delivery', 'kiosk']"
    )
    exclude_channels = models.JSONField(default=list, blank=True)
    
    # Customer Acquisition
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='all')
    inactive_days_threshold = models.IntegerField(default=30)
    
    # Employee/Manual
    is_employee_promo = models.BooleanField(default=False)
    employee_roles = models.JSONField(default=list, blank=True)
    require_manager_approval = models.BooleanField(default=False)
    require_approval_pin = models.BooleanField(default=False)
    allow_manual_override = models.BooleanField(default=False)
    max_manual_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_manual_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    override_requires_approval = models.BooleanField(default=False)
    override_approval_roles = models.JSONField(default=list, blank=True)
    
    # Upsell
    is_upsell = models.BooleanField(default=False)
    required_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='upsell_required_promotions',
        null=True,
        blank=True
    )
    upsell_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='upsell_offer_promotions',
        null=True,
        blank=True
    )
    upsell_special_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    upsell_message = models.TextField(blank=True)
    
    # Mix & Match
    is_mix_match = models.BooleanField(default=False)
    mix_match_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON: rules for mix & match"
    )
    
    # Conflict Resolution
    execution_priority = models.IntegerField(
        default=500,
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        help_text="1-999, lower executes first"
    )
    execution_stage = models.CharField(
        max_length=20,
        choices=EXECUTION_STAGE_CHOICES,
        default='item_level'
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_auto_apply = models.BooleanField(default=True, help_text="Auto-apply when conditions met")
    require_voucher = models.BooleanField(default=False)
    show_in_menu = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_promotions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promotion'
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        ordering = ['-execution_priority', '-created_at']
        indexes = [
            models.Index(fields=['company', 'is_active', 'start_date', 'end_date']),
            models.Index(fields=['scope', 'is_active']),
            models.Index(fields=['promo_type']),
            models.Index(fields=['code']),
            models.Index(fields=['execution_priority']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid_now(self):
        """Check if promotion is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now.date() <= self.end_date
        )


class PackagePromotion(models.Model):
    """
    Package/Set Menu Promotion
    Example: Paket Hemat = Nasi + Ayam + Drink = 35k
    """
    DEDUCTION_STRATEGY_CHOICES = [
        ('fixed_only', 'Fixed Items Only'),
        ('selected_only', 'Selected Items Only'),
        ('all_components', 'All Components'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promotion = models.OneToOneField(Promotion, on_delete=models.CASCADE, related_name='package')
    package_name = models.CharField(max_length=200)
    package_sku = models.CharField(max_length=50, unique=True)
    package_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='package_promotions/', null=True, blank=True)
    description = models.TextField(blank=True)
    
    allow_modification = models.BooleanField(default=False)
    min_items_required = models.IntegerField(default=0)
    max_items_allowed = models.IntegerField(default=0)
    
    track_as_virtual_product = models.BooleanField(default=False)
    auto_deduct_components = models.BooleanField(default=True)
    deduction_strategy = models.CharField(
        max_length=20,
        choices=DEDUCTION_STRATEGY_CHOICES,
        default='all_components'
    )
    
    class Meta:
        db_table = 'package_promotion'
        verbose_name = 'Package Promotion'
        verbose_name_plural = 'Package Promotions'
        indexes = [
            models.Index(fields=['package_sku']),
        ]
    
    def __str__(self):
        return f"{self.package_sku} - {self.package_name}"


class PackageItem(models.Model):
    """
    Package Components - Fixed or Choice items
    """
    ITEM_TYPE_CHOICES = [
        ('fixed', 'Fixed Item'),
        ('choice', 'Choice Item'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PackagePromotion, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="For fixed items"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="For choice items (choose from category)"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_required = models.BooleanField(default=True)
    min_selection = models.IntegerField(default=0)
    max_selection = models.IntegerField(default=1)
    upsell_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    upsell_options = models.JSONField(default=list, blank=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'package_item'
        verbose_name = 'Package Item'
        verbose_name_plural = 'Package Items'
        ordering = ['sort_order']
        unique_together = [['package', 'sort_order']]
    
    def __str__(self):
        if self.product:
            return f"{self.package.package_name} - {self.product.name}"
        return f"{self.package.package_name} - {self.category.name} (choice)"


class PromotionTier(models.Model):
    """
    Multi-Tier Threshold Promotion
    Example: >100k=10k off, >200k=25k off
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percent Discount'),
        ('amount', 'Amount Discount'),
        ('free_product', 'Free Product'),
        ('points_multiplier', 'Points Multiplier'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='tiers')
    tier_name = models.CharField(max_length=200)
    tier_order = models.IntegerField()
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='tier_free_products'
    )
    points_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'promotion_tier'
        verbose_name = 'Promotion Tier'
        verbose_name_plural = 'Promotion Tiers'
        ordering = ['tier_order']
        unique_together = [['promotion', 'tier_order']]
        indexes = [
            models.Index(fields=['promotion', 'min_amount', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.promotion.name} - {self.tier_name}"


class Voucher(models.Model):
    """
    Voucher - Generated codes for promotions
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name='vouchers')
    code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    qr_code = models.CharField(max_length=200, blank=True)
    
    # Usage tracking (updated by Edge)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='used_vouchers'
    )
    used_bill = models.UUIDField(null=True, blank=True, help_text="Reference to Bill")
    
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voucher'
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['promotion', 'status']),
            models.Index(fields=['code']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.promotion.name}"


# Models below are for tracking/logging (received from Edge)

class PromotionUsage(models.Model):
    """
    Promotion Usage Tracking (received from Edge)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name='usages')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, null=True, blank=True, related_name='promotion_usages')
    customer_phone = models.CharField(max_length=20, blank=True)
    bill_id = models.UUIDField(help_text="Reference to Bill")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='promotion_usages')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'promotion_usage'
        verbose_name = 'Promotion Usage'
        verbose_name_plural = 'Promotion Usages'
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['promotion', 'member', 'used_at']),
            models.Index(fields=['promotion', 'customer_phone', 'used_at']),
            models.Index(fields=['promotion', 'used_at']),
        ]
    
    def __str__(self):
        return f"{self.promotion.code} - {self.used_at}"


class PromotionLog(models.Model):
    """
    Promotion Log - Explainability (applied/skipped/failed)
    Received from Edge for analysis
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('skipped', 'Skipped'),
        ('failed', 'Failed'),
        ('override', 'Manager Override'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_id = models.UUIDField(help_text="Reference to Bill")
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name='logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(help_text="Why applied/skipped/failed")
    validation_details = models.JSONField(default=dict, blank=True)
    original_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approved_promotion_logs'
    )
    approval_pin_entered = models.BooleanField(default=False)
    override_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'promotion_log'
        verbose_name = 'Promotion Log'
        verbose_name_plural = 'Promotion Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bill_id', 'status']),
            models.Index(fields=['promotion', 'status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.promotion.code} - {self.status}"


class CustomerPromotionHistory(models.Model):
    """
    First Order Tracking per Brand
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, null=True, blank=True, related_name='promotion_history')
    customer_phone = models.CharField(max_length=20, db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='customer_promotion_history')
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name='customer_history')
    first_order_date = models.DateTimeField()
    first_bill_id = models.UUIDField()
    last_order_date = models.DateTimeField()
    total_orders = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'customer_promotion_history'
        verbose_name = 'Customer Promotion History'
        verbose_name_plural = 'Customer Promotion Histories'
        unique_together = [['member', 'brand', 'promotion']]
        indexes = [
            models.Index(fields=['customer_phone', 'brand']),
            models.Index(fields=['member', 'last_order_date']),
        ]
    
    def __str__(self):
        return f"{self.customer_phone} - {self.brand.name}"


class PromotionApproval(models.Model):
    """
    Manager Override/Approval Workflow
    """
    REQUEST_TYPE_CHOICES = [
        ('manual_discount', 'Manual Discount'),
        ('employee_promo', 'Employee Promo'),
        ('override', 'Override Rules'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_id = models.UUIDField(help_text="Reference to Bill")
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approvals'
    )
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='promotion_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    request_reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='promotion_approvals'
    )
    approval_pin = models.CharField(max_length=6, blank=True)
    approval_notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'promotion_approval'
        verbose_name = 'Promotion Approval'
        verbose_name_plural = 'Promotion Approvals'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['bill_id', 'status']),
            models.Index(fields=['requested_by', 'requested_at']),
        ]
    
    def __str__(self):
        return f"{self.request_type} - {self.status}"
    
    def approve(self, user, pin, notes=''):
        """Approve request with authorization check"""
        # Authorization check based on role_scope
        if not self._can_user_approve(user):
            raise PermissionError(f"User {user.username} cannot approve this request")
        
        if user.pin != pin:
            raise ValueError("Invalid PIN")
        
        self.approved_by = user
        self.approval_pin = pin
        self.approval_notes = notes
        self.status = 'approved'
        self.responded_at = timezone.now()
        self.save()
    
    def reject(self, user, notes=''):
        """Reject request"""
        if not self._can_user_approve(user):
            raise PermissionError(f"User {user.username} cannot reject this request")
        
        self.approved_by = user
        self.approval_notes = notes
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
    
    def _can_user_approve(self, user):
        """Check if user can approve based on role_scope"""
        # Implementation depends on bill's brand
        # For now, simplified version
        if user.role_scope == 'company':
            return True  # Company scope can approve all
        # TODO: Check brand match for brand/store scope
        return True
