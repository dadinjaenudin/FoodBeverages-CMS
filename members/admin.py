"""
Admin configuration for Members app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Member, MemberTransaction


class MemberTransactionInline(admin.TabularInline):
    model = MemberTransaction
    extra = 0
    can_delete = False
    readonly_fields = ['transaction_type', 'points_change', 'points_before', 'points_after',
                       'balance_change', 'balance_before', 'balance_after', 'reference', 'notes', 'created_by', 'created_at']
    fields = readonly_fields
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['member_code', 'full_name', 'phone', 'company', 'tier', 'points', 'point_balance', 
                    'total_visits', 'total_spent', 'is_active', 'joined_date']
    list_filter = ['company', 'tier', 'is_active', 'gender', 'joined_date']
    search_fields = ['member_code', 'full_name', 'phone', 'email', 'card_number']
    readonly_fields = ['id', 'member_code', 'points', 'point_balance', 'total_visits', 'total_spent', 
                       'last_visit', 'created_at', 'updated_at', 'get_point_expiry']
    autocomplete_fields = ['company', 'created_by']
    inlines = [MemberTransactionInline]
    
    fieldsets = (
        ('Membership', {
            'fields': ('id', 'company', 'member_code', 'card_number', 'tier', 'joined_date', 
                       'expire_date', 'is_active')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone', 'birth_date', 'gender')
        }),
        ('Address', {
            'fields': ('address', 'city', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Loyalty Program', {
            'fields': ('points', 'point_balance', 'get_point_expiry')
        }),
        ('Statistics (from Edge)', {
            'fields': ('total_visits', 'total_spent', 'last_visit'),
            'description': 'Statistics updated by Edge Server'
        }),
        ('Record Info', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_point_expiry(self, obj):
        """Display point expiry date"""
        expiry_date = obj.get_point_expiry_date()
        if expiry_date is None:
            return format_html('<span style="color: green;">Never expires</span>')
        
        if expiry_date < timezone.now().date():
            return format_html('<span style="color: red;">{} (Expired)</span>', expiry_date)
        elif expiry_date < (timezone.now().date() + timezone.timedelta(days=30)):
            return format_html('<span style="color: orange;">{} (Expiring soon)</span>', expiry_date)
        else:
            return format_html('<span>{}</span>', expiry_date)
    get_point_expiry.short_description = 'Point Expiry Date'
    
    actions = ['export_members', 'activate_members', 'deactivate_members']
    
    def export_members(self, request, queryset):
        """Export selected members"""
        # TODO: Implement CSV export
        self.message_user(request, f"{queryset.count()} members selected for export")
    export_members.short_description = "Export selected members"
    
    def activate_members(self, request, queryset):
        """Activate selected members"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} members activated")
    activate_members.short_description = "Activate selected members"
    
    def deactivate_members(self, request, queryset):
        """Deactivate selected members"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} members deactivated")
    deactivate_members.short_description = "Deactivate selected members"


@admin.register(MemberTransaction)
class MemberTransactionAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'member', 'transaction_type', 'points_change', 'points_after', 
                    'balance_change', 'balance_after', 'reference', 'created_by']
    list_filter = ['transaction_type', 'created_at', 'member__company']
    search_fields = ['member__member_code', 'member__full_name', 'reference', 'notes']
    readonly_fields = ['id', 'member', 'bill_id', 'transaction_type', 'points_change', 'points_before', 
                       'points_after', 'balance_change', 'balance_before', 'balance_after', 'reference', 
                       'notes', 'created_by', 'created_at']
    autocomplete_fields = []
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('id', 'member', 'bill_id', 'transaction_type', 'created_at')
        }),
        ('Points', {
            'fields': ('points_change', 'points_before', 'points_after')
        }),
        ('Balance', {
            'fields': ('balance_change', 'balance_before', 'balance_after')
        }),
        ('Audit Trail', {
            'fields': ('reference', 'notes', 'created_by')
        }),
    )
    
    def has_add_permission(self, request):
        """Transactions should be created via Member methods, not directly"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Transactions should not be deleted for audit trail"""
        return False
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('member', 'created_by')
