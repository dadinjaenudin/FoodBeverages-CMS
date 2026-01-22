"""
Transaction Models - Data received from Edge Servers
HO receives transactional data from Edge (Bill, BillItem, Payment, etc.)
Edge → HO push async
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Bill(models.Model):
    """Bill/Invoice - Main transaction document"""
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('PAID', 'Paid'),
        ('VOID', 'Void'),
        ('REFUND', 'Refund'),
        ('PARTIAL_REFUND', 'Partial Refund'),
    ]
    
    BILL_TYPE_CHOICES = [
        ('DINE_IN', 'Dine In'),
        ('TAKEAWAY', 'Takeaway'),
        ('DELIVERY', 'Delivery'),
        ('QRORDER', 'QR Order'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Denormalized for HO reporting
    company_id = models.UUIDField(db_index=True)
    brand_id = models.UUIDField(db_index=True)
    store_id = models.UUIDField(db_index=True)
    terminal_id = models.UUIDField()
    
    bill_number = models.CharField(max_length=50, unique=True, db_index=True)
    bill_type = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', db_index=True)
    
    # Table info (nullable for non dine-in)
    table_id = models.UUIDField(null=True, blank=True)
    table_number = models.CharField(max_length=20, null=True, blank=True)
    pax = models.PositiveIntegerField(default=1)
    
    # Member info
    member_id = models.UUIDField(null=True, blank=True, db_index=True)
    member_code = models.CharField(max_length=50, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rounding_adjustment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Audit trail
    created_by = models.UUIDField()
    created_at = models.DateTimeField(db_index=True)
    closed_by = models.UUIDField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.UUIDField(null=True, blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_reason = models.TextField(null=True, blank=True)
    
    # Sync metadata
    synced_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bill'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_id', 'created_at'], name='bill_company_date_idx'),
            models.Index(fields=['brand_id', 'store_id', 'status', 'created_at'], name='bill_brand_store_idx'),
            models.Index(fields=['bill_number'], name='bill_number_idx'),
            models.Index(fields=['status', 'created_at'], name='bill_status_date_idx'),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {self.status}"


class BillItem(models.Model):
    """Bill line items - products ordered"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT_TO_KITCHEN', 'Sent to Kitchen'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
        ('VOID', 'Void'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_id = models.UUIDField(db_index=True)
    
    # Denormalized for HO reporting
    company_id = models.UUIDField(db_index=True)
    brand_id = models.UUIDField(db_index=True)
    store_id = models.UUIDField(db_index=True)
    
    product_id = models.UUIDField()
    product_sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=300)
    category_id = models.UUIDField(null=True, blank=True)
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_void = models.BooleanField(default=False, db_index=True)
    void_reason = models.TextField(null=True, blank=True)
    
    # Modifiers snapshot (JSON)
    modifiers_snapshot = models.JSONField(default=list, blank=True)
    
    # Kitchen
    kitchen_station_id = models.UUIDField(null=True, blank=True)
    sent_to_kitchen_at = models.DateTimeField(null=True, blank=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(db_index=True)
    created_by = models.UUIDField()
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.UUIDField(null=True, blank=True)
    
    class Meta:
        db_table = 'bill_item'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['bill_id', 'is_void', 'status'], name='billitem_bill_status_idx'),
            models.Index(fields=['company_id', 'brand_id', 'created_at'], name='billitem_company_idx'),
            models.Index(fields=['product_id', 'created_at'], name='billitem_product_idx'),
        ]
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class Payment(models.Model):
    """Payment records - multi-payment support"""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('QRIS', 'QRIS'),
        ('EWALLET', 'E-Wallet'),
        ('TRANSFER', 'Bank Transfer'),
        ('VOUCHER', 'Voucher'),
        ('MEMBER_POINTS', 'Member Points'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUND', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_id = models.UUIDField(db_index=True)
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # For cash
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    change = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # External reference
    external_reference = models.CharField(max_length=200, null=True, blank=True)
    payment_gateway_response = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(db_index=True)
    created_by = models.UUIDField()
    
    class Meta:
        db_table = 'payment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bill_id', 'created_at'], name='payment_bill_idx'),
            models.Index(fields=['payment_method', 'status'], name='payment_method_status_idx'),
        ]
    
    def __str__(self):
        return f"{self.payment_method} - {self.amount}"


class BillPromotion(models.Model):
    """Applied promotions on bill"""
    EXECUTION_STAGE_CHOICES = [
        ('ITEM_LEVEL', 'Item Level'),
        ('SUBTOTAL', 'Subtotal'),
        ('PAYMENT', 'Payment'),
        ('CASHBACK', 'Cashback'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_id = models.UUIDField(db_index=True)
    promotion_id = models.UUIDField()
    promotion_name = models.CharField(max_length=300)
    promotion_code = models.CharField(max_length=100, null=True, blank=True)
    
    execution_stage = models.CharField(max_length=50, choices=EXECUTION_STAGE_CHOICES)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cashback_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Affected items (JSON array of BillItem IDs)
    affected_items = models.JSONField(default=list, blank=True)
    
    # Explainability
    calculation_detail = models.JSONField(null=True, blank=True)
    
    applied_at = models.DateTimeField(db_index=True)
    applied_by = models.UUIDField()
    
    class Meta:
        db_table = 'bill_promotion'
        ordering = ['applied_at']
        indexes = [
            models.Index(fields=['bill_id', 'applied_at'], name='billpromo_bill_idx'),
            models.Index(fields=['promotion_id', 'applied_at'], name='billpromo_promo_idx'),
        ]
    
    def __str__(self):
        return f"{self.promotion_name} - {self.discount_amount}"


class CashDrop(models.Model):
    """Cash drop/pickup records"""
    TRANSACTION_TYPE_CHOICES = [
        ('DROP', 'Drop'),
        ('PICKUP', 'Pickup'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Denormalized
    company_id = models.UUIDField(db_index=True)
    brand_id = models.UUIDField(db_index=True)
    store_id = models.UUIDField(db_index=True)
    terminal_id = models.UUIDField()
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(db_index=True)
    created_by = models.UUIDField()
    
    class Meta:
        db_table = 'cash_drop'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_id', 'brand_id', 'store_id', 'created_at'], name='cashdrop_store_idx'),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class StoreSession(models.Model):
    """Store daily session - EOD"""
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store_id = models.UUIDField(db_index=True)
    brand_id = models.UUIDField(db_index=True)
    company_id = models.UUIDField(db_index=True)
    
    session_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # Summary
    opening_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_refund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    opened_at = models.DateTimeField()
    opened_by = models.UUIDField()
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.UUIDField(null=True, blank=True)
    
    class Meta:
        db_table = 'store_session'
        ordering = ['-session_date']
        indexes = [
            models.Index(fields=['store_id', 'session_date'], name='session_store_date_idx'),
            models.Index(fields=['company_id', 'session_date'], name='session_company_date_idx'),
        ]
        unique_together = [['store_id', 'session_date']]
    
    def __str__(self):
        return f"Session {self.session_date} - {self.status}"


class CashierShift(models.Model):
    """Cashier shift - per user per terminal"""
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store_session_id = models.UUIDField(db_index=True)
    terminal_id = models.UUIDField(db_index=True)
    cashier_id = models.UUIDField(db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    opening_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    opened_at = models.DateTimeField(db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cashier_shift'
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['store_session_id', 'terminal_id'], name='shift_session_terminal_idx'),
            models.Index(fields=['cashier_id', 'opened_at'], name='shift_cashier_idx'),
        ]
    
    def __str__(self):
        return f"Shift {self.cashier_id} - {self.opened_at}"


class KitchenOrder(models.Model):
    """Kitchen order - printed orders"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_id = models.UUIDField(db_index=True)
    bill_item_id = models.UUIDField()
    
    kitchen_station_id = models.UUIDField(db_index=True)
    product_name = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    printed_at = models.DateTimeField(db_index=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'kitchen_order'
        ordering = ['printed_at']
        indexes = [
            models.Index(fields=['bill_id', 'status'], name='kitchen_bill_status_idx'),
            models.Index(fields=['kitchen_station_id', 'status', 'printed_at'], name='kitchen_station_idx'),
        ]
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity} - {self.status}"


class BillRefund(models.Model):
    """Refund records - partial or full"""
    REFUND_TYPE_CHOICES = [
        ('FULL', 'Full Refund'),
        ('PARTIAL', 'Partial Refund'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_bill_id = models.UUIDField(db_index=True)
    refund_bill_id = models.UUIDField(null=True, blank=True)  # New bill for refund
    
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPE_CHOICES)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Refunded items (JSON)
    refunded_items = models.JSONField(default=list, blank=True)
    
    requested_at = models.DateTimeField(db_index=True)
    requested_by = models.UUIDField()
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.UUIDField(null=True, blank=True)
    approval_notes = models.TextField(null=True, blank=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'bill_refund'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['original_bill_id', 'status'], name='refund_bill_status_idx'),
            models.Index(fields=['status', 'requested_at'], name='refund_status_date_idx'),
        ]
    
    def __str__(self):
        return f"Refund {self.refund_type} - {self.refund_amount}"


class InventoryMovement(models.Model):
    """Inventory movement records from Edge"""
    MOVEMENT_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('REFUND', 'Refund'),
        ('WASTE', 'Waste'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('MANUFACTURING', 'Manufacturing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store_id = models.UUIDField(db_index=True)
    brand_id = models.UUIDField(db_index=True)
    company_id = models.UUIDField(db_index=True)
    
    inventory_item_id = models.UUIDField(db_index=True)
    movement_type = models.CharField(max_length=50, choices=MOVEMENT_TYPE_CHOICES)
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Reference
    bill_id = models.UUIDField(null=True, blank=True)
    bill_item_id = models.UUIDField(null=True, blank=True)
    recipe_id = models.UUIDField(null=True, blank=True)
    
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(db_index=True)
    created_by = models.UUIDField()
    
    class Meta:
        db_table = 'inventory_movement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item_id', 'created_at'], name='invmov_item_date_idx'),
            models.Index(fields=['store_id', 'movement_type', 'created_at'], name='invmov_store_type_idx'),
            models.Index(fields=['bill_id'], name='invmov_bill_idx'),
        ]
    
    def __str__(self):
        return f"{self.movement_type} - {self.quantity} {self.unit}"
