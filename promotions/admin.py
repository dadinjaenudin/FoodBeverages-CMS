"""
Admin configuration for Promotions app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Promotion, PackagePromotion, PackageItem, PromotionTier,
    Voucher, PromotionUsage, PromotionLog, CustomerPromotionHistory,
    PromotionApproval
)


class PackageItemInline(admin.TabularInline):
    model = PackageItem
    extra = 1
    autocomplete_fields = ['product', 'category']
    fields = ['item_type', 'product', 'category', 'quantity', 'is_required', 'min_selection', 'max_selection', 'sort_order']


class PromotionTierInline(admin.TabularInline):
    model = PromotionTier
    extra = 1
    fields = ['tier_name', 'tier_order', 'min_amount', 'max_amount', 'discount_type', 'discount_value', 'is_active']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'company', 'promo_type', 'scope', 'is_active', 'start_date', 'end_date', 'priority']
    list_filter = ['company', 'promo_type', 'scope', 'is_active', 'start_date', 'end_date']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['id', 'current_uses', 'created_at', 'updated_at']
    autocomplete_fields = ['company', 'brand', 'created_by', 'get_product', 'required_product', 'upsell_product']
    filter_horizontal = ['brands', 'exclude_brands', 'combo_products', 'categories', 'products', 
                         'exclude_categories', 'exclude_products', 'exclude_members', 'cannot_combine_with']
    inlines = [PromotionTierInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'company', 'code', 'name', 'description', 'terms_conditions', 'is_active')
        }),
        ('Promotion Type', {
            'fields': ('promo_type', 'apply_to')
        }),
        ('Multi-Brand Scope', {
            'fields': ('scope', 'brand', 'brands', 'exclude_brands'),
            'classes': ('collapse',)
        }),
        ('Discount Configuration', {
            'fields': ('discount_percent', 'discount_amount', 'max_discount_amount'),
            'classes': ('collapse',)
        }),
        ('BOGO Configuration', {
            'fields': ('buy_quantity', 'get_quantity', 'get_product'),
            'classes': ('collapse',)
        }),
        ('Combo/Happy Hour', {
            'fields': ('combo_price', 'combo_products', 'happy_hour_price'),
            'classes': ('collapse',)
        }),
        ('Payment Method', {
            'fields': ('payment_methods', 'payment_min_amount'),
            'classes': ('collapse',)
        }),
        ('Product/Category Filters', {
            'fields': ('categories', 'products', 'exclude_categories', 'exclude_products'),
            'classes': ('collapse',)
        }),
        ('Member Configuration', {
            'fields': ('member_only', 'member_tiers', 'exclude_members'),
            'classes': ('collapse',)
        }),
        ('Time Rules', {
            'fields': ('start_date', 'end_date', 'valid_days', 'valid_time_start', 'valid_time_end', 'exclude_holidays')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'max_uses_per_customer', 'max_uses_per_day', 'current_uses')
        }),
        ('Requirements', {
            'fields': ('min_purchase', 'min_quantity', 'min_items'),
            'classes': ('collapse',)
        }),
        ('Stacking & Priority', {
            'fields': ('is_stackable', 'priority', 'cannot_combine_with', 'execution_priority', 'execution_stage')
        }),
        ('Channel & Customer', {
            'fields': ('sales_channels', 'exclude_channels', 'customer_type', 'inactive_days_threshold'),
            'classes': ('collapse',)
        }),
        ('Employee/Manual', {
            'fields': ('is_employee_promo', 'employee_roles', 'require_manager_approval', 'require_approval_pin',
                       'allow_manual_override', 'max_manual_discount_percent', 'max_manual_discount_amount',
                       'override_requires_approval', 'override_approval_roles'),
            'classes': ('collapse',)
        }),
        ('Upsell', {
            'fields': ('is_upsell', 'required_product', 'upsell_product', 'upsell_special_price', 'upsell_message'),
            'classes': ('collapse',)
        }),
        ('Mix & Match', {
            'fields': ('is_mix_match', 'mix_match_rules'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_auto_apply', 'require_voucher', 'show_in_menu')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['duplicate_promotion', 'activate_promotions', 'deactivate_promotions']
    
    def duplicate_promotion(self, request, queryset):
        """Duplicate selected promotions"""
        for promo in queryset:
            # TODO: Implement duplication logic
            pass
        self.message_user(request, f"{queryset.count()} promotions selected for duplication")
    duplicate_promotion.short_description = "Duplicate selected promotions"
    
    def activate_promotions(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} promotions activated")
    activate_promotions.short_description = "Activate selected promotions"
    
    def deactivate_promotions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} promotions deactivated")
    deactivate_promotions.short_description = "Deactivate selected promotions"


@admin.register(PackagePromotion)
class PackagePromotionAdmin(admin.ModelAdmin):
    list_display = ['package_sku', 'package_name', 'package_price', 'promotion', 'deduction_strategy']
    list_filter = ['deduction_strategy', 'track_as_virtual_product']
    search_fields = ['package_sku', 'package_name', 'promotion__name']
    readonly_fields = ['id']
    autocomplete_fields = ['promotion']
    inlines = [PackageItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'promotion', 'package_sku', 'package_name', 'package_price', 'image', 'description')
        }),
        ('Configuration', {
            'fields': ('allow_modification', 'min_items_required', 'max_items_allowed')
        }),
        ('Inventory Tracking', {
            'fields': ('track_as_virtual_product', 'auto_deduct_components', 'deduction_strategy')
        }),
    )


@admin.register(PromotionTier)
class PromotionTierAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'tier_name', 'tier_order', 'min_amount', 'max_amount', 'discount_type', 'discount_value', 'is_active']
    list_filter = ['promotion', 'discount_type', 'is_active']
    search_fields = ['tier_name', 'promotion__name']
    readonly_fields = ['id']
    autocomplete_fields = ['promotion', 'free_product']


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['code', 'promotion', 'status', 'customer_phone', 'expires_at', 'used_at']
    list_filter = ['status', 'promotion', 'expires_at']
    search_fields = ['code', 'customer_phone', 'customer_name']
    readonly_fields = ['id', 'used_at', 'used_by', 'used_bill', 'created_at']
    autocomplete_fields = ['promotion', 'used_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Voucher Info', {
            'fields': ('id', 'promotion', 'code', 'status', 'qr_code', 'expires_at')
        }),
        ('Customer', {
            'fields': ('customer_phone', 'customer_name')
        }),
        ('Usage (from Edge)', {
            'fields': ('used_at', 'used_by', 'used_bill'),
            'description': 'Usage data updated by Edge Server'
        }),
        ('Audit', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_qr_codes', 'expire_vouchers']
    
    def generate_qr_codes(self, request, queryset):
        """Generate QR codes for vouchers"""
        # TODO: Implement QR generation
        self.message_user(request, f"QR codes generated for {queryset.count()} vouchers")
    generate_qr_codes.short_description = "Generate QR codes"
    
    def expire_vouchers(self, request, queryset):
        count = queryset.update(status='expired')
        self.message_user(request, f"{count} vouchers expired")
    expire_vouchers.short_description = "Mark as expired"


@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'member', 'customer_phone', 'brand', 'discount_amount', 'used_at']
    list_filter = ['promotion', 'brand', 'used_at']
    search_fields = ['promotion__name', 'customer_phone', 'member__full_name']
    readonly_fields = ['id', 'promotion', 'member', 'customer_phone', 'bill_id', 'brand', 'discount_amount', 'used_at']
    date_hierarchy = 'used_at'
    
    def has_add_permission(self, request):
        return False  # Created by Edge
    
    def has_delete_permission(self, request, obj=None):
        return False  # Audit trail


@admin.register(PromotionLog)
class PromotionLogAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'bill_id', 'status', 'discount_amount', 'approved_by', 'created_at']
    list_filter = ['status', 'promotion', 'created_at']
    search_fields = ['bill_id', 'promotion__name', 'reason']
    readonly_fields = ['id', 'bill_id', 'promotion', 'status', 'reason', 'validation_details',
                       'original_amount', 'discount_amount', 'final_amount', 'approved_by',
                       'approval_pin_entered', 'override_reason', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CustomerPromotionHistory)
class CustomerPromotionHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer_phone', 'brand', 'promotion', 'first_order_date', 'total_orders']
    list_filter = ['brand', 'promotion', 'first_order_date']
    search_fields = ['customer_phone', 'member__full_name']
    readonly_fields = ['id', 'member', 'customer_phone', 'brand', 'promotion', 
                       'first_order_date', 'first_bill_id', 'last_order_date', 'total_orders']


@admin.register(PromotionApproval)
class PromotionApprovalAdmin(admin.ModelAdmin):
    list_display = ['bill_id', 'request_type', 'requested_by', 'requested_amount', 'status', 'approved_by', 'requested_at']
    list_filter = ['request_type', 'status', 'requested_at']
    search_fields = ['bill_id', 'requested_by__username', 'approved_by__username']
    readonly_fields = ['id', 'bill_id', 'promotion', 'requested_by', 'request_type', 'requested_amount',
                       'request_reason', 'status', 'approved_by', 'approval_pin', 'approval_notes',
                       'requested_at', 'responded_at']
    autocomplete_fields = ['promotion', 'requested_by', 'approved_by']
    date_hierarchy = 'requested_at'
