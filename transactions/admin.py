"""
Transaction Admin - Read-only views for HO
All data received from Edge servers
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Bill, BillItem, Payment, BillPromotion, CashDrop,
    StoreSession, CashierShift, KitchenOrder, BillRefund, InventoryMovement
)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'bill_type', 'status', 'total', 'customer_name', 'created_at', 'synced_at']
    list_filter = ['status', 'bill_type', 'created_at', 'synced_at']
    search_fields = ['bill_number', 'customer_name', 'customer_phone', 'member_code']
    readonly_fields = [
        'id', 'company_id', 'brand_id', 'store_id', 'terminal_id',
        'bill_number', 'bill_type', 'status', 'table_id', 'table_number', 'pax',
        'member_id', 'member_code', 'customer_name', 'customer_phone',
        'subtotal', 'tax_rate', 'tax_amount', 'service_charge_rate', 'service_charge',
        'discount_amount', 'total', 'rounding_adjustment',
        'created_by', 'created_at', 'closed_by', 'closed_at',
        'voided_by', 'voided_at', 'voided_reason', 'synced_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'quantity', 'unit_price', 'total', 'status', 'is_void', 'created_at']
    list_filter = ['status', 'is_void', 'created_at']
    search_fields = ['product_name', 'product_sku']
    readonly_fields = [
        'id', 'bill_id', 'company_id', 'brand_id', 'store_id',
        'product_id', 'product_sku', 'product_name', 'category_id',
        'quantity', 'unit_price', 'unit_cost', 'discount_amount', 'total',
        'notes', 'status', 'is_void', 'void_reason',
        'modifiers_snapshot', 'kitchen_station_id',
        'sent_to_kitchen_at', 'prepared_at',
        'created_at', 'created_by', 'voided_at', 'voided_by'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['bill_id', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['external_reference']
    readonly_fields = [
        'id', 'bill_id', 'payment_method', 'amount', 'status',
        'cash_received', 'change', 'external_reference', 'payment_gateway_response',
        'created_at', 'created_by'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BillPromotion)
class BillPromotionAdmin(admin.ModelAdmin):
    list_display = ['promotion_name', 'bill_id', 'execution_stage', 'discount_amount', 'cashback_amount', 'applied_at']
    list_filter = ['execution_stage', 'applied_at']
    search_fields = ['promotion_name', 'promotion_code']
    readonly_fields = [
        'id', 'bill_id', 'promotion_id', 'promotion_name', 'promotion_code',
        'execution_stage', 'discount_amount', 'cashback_amount',
        'affected_items', 'calculation_detail', 'applied_at', 'applied_by'
    ]
    date_hierarchy = 'applied_at'
    ordering = ['-applied_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CashDrop)
class CashDropAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'store_id', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    readonly_fields = [
        'id', 'company_id', 'brand_id', 'store_id', 'terminal_id',
        'transaction_type', 'amount', 'notes', 'created_at', 'created_by'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StoreSession)
class StoreSessionAdmin(admin.ModelAdmin):
    list_display = ['session_date', 'store_id', 'status', 'total_sales', 'variance', 'opened_at']
    list_filter = ['status', 'session_date']
    readonly_fields = [
        'id', 'store_id', 'brand_id', 'company_id', 'session_date', 'status',
        'opening_cash', 'closing_cash', 'expected_cash', 'variance',
        'total_sales', 'total_discount', 'total_refund',
        'opened_at', 'opened_by', 'closed_at', 'closed_by'
    ]
    date_hierarchy = 'session_date'
    ordering = ['-session_date']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CashierShift)
class CashierShiftAdmin(admin.ModelAdmin):
    list_display = ['cashier_id', 'terminal_id', 'status', 'variance', 'opened_at']
    list_filter = ['status', 'opened_at']
    readonly_fields = [
        'id', 'store_session_id', 'terminal_id', 'cashier_id', 'status',
        'opening_cash', 'closing_cash', 'expected_cash', 'variance',
        'opened_at', 'closed_at'
    ]
    date_hierarchy = 'opened_at'
    ordering = ['-opened_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(KitchenOrder)
class KitchenOrderAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'quantity', 'status', 'kitchen_station_id', 'printed_at']
    list_filter = ['status', 'printed_at']
    search_fields = ['product_name']
    readonly_fields = [
        'id', 'bill_id', 'bill_item_id', 'kitchen_station_id',
        'product_name', 'quantity', 'notes', 'status',
        'printed_at', 'prepared_at', 'served_at'
    ]
    date_hierarchy = 'printed_at'
    ordering = ['-printed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BillRefund)
class BillRefundAdmin(admin.ModelAdmin):
    list_display = ['original_bill_id', 'refund_type', 'refund_amount', 'status', 'requested_at']
    list_filter = ['refund_type', 'status', 'requested_at']
    readonly_fields = [
        'id', 'original_bill_id', 'refund_bill_id', 'refund_type', 'refund_amount',
        'reason', 'status', 'refunded_items',
        'requested_at', 'requested_by', 'approved_at', 'approved_by',
        'approval_notes', 'completed_at'
    ]
    date_hierarchy = 'requested_at'
    ordering = ['-requested_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['movement_type', 'inventory_item_id', 'quantity', 'unit', 'total_cost', 'created_at']
    list_filter = ['movement_type', 'created_at']
    readonly_fields = [
        'id', 'store_id', 'brand_id', 'company_id',
        'inventory_item_id', 'movement_type',
        'quantity', 'unit', 'unit_cost', 'total_cost',
        'bill_id', 'bill_item_id', 'recipe_id',
        'notes', 'created_at', 'created_by'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
