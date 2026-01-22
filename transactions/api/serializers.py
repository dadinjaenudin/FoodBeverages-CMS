"""
Transactions API Serializers - For Edge → HO Push
Receive transaction data from Edge servers
"""
from rest_framework import serializers
from transactions.models import (
    Bill, BillItem, Payment, BillPromotion, CashDrop,
    StoreSession, CashierShift, KitchenOrder, BillRefund, InventoryMovement
)


class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class BillPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPromotion
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, required=False, source='billitem_set')
    payments = PaymentSerializer(many=True, required=False, source='payment_set')
    promotions = BillPromotionSerializer(many=True, required=False, source='billpromotion_set')
    
    class Meta:
        model = Bill
        fields = '__all__'
    
    def create(self, validated_data):
        items_data = validated_data.pop('billitem_set', [])
        payments_data = validated_data.pop('payment_set', [])
        promotions_data = validated_data.pop('billpromotion_set', [])
        
        # Create bill
        bill = Bill.objects.create(**validated_data)
        
        # Create related items
        for item_data in items_data:
            BillItem.objects.create(bill_id=bill.id, **item_data)
        
        for payment_data in payments_data:
            Payment.objects.create(bill_id=bill.id, **payment_data)
        
        for promo_data in promotions_data:
            BillPromotion.objects.create(bill_id=bill.id, **promo_data)
        
        return bill


class CashDropSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashDrop
        fields = '__all__'


class StoreSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSession
        fields = '__all__'


class CashierShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashierShift
        fields = '__all__'


class KitchenOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenOrder
        fields = '__all__'


class BillRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillRefund
        fields = '__all__'


class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = '__all__'


class BulkTransactionSerializer(serializers.Serializer):
    """Bulk transaction push from Edge - multiple records in one request"""
    bills = BillSerializer(many=True, required=False)
    cash_drops = CashDropSerializer(many=True, required=False)
    store_sessions = StoreSessionSerializer(many=True, required=False)
    cashier_shifts = CashierShiftSerializer(many=True, required=False)
    kitchen_orders = KitchenOrderSerializer(many=True, required=False)
    bill_refunds = BillRefundSerializer(many=True, required=False)
    inventory_movements = InventoryMovementSerializer(many=True, required=False)
    
    def create(self, validated_data):
        """Create all records in bulk"""
        created_counts = {}
        
        # Bills (with nested items/payments/promotions)
        bills_data = validated_data.get('bills', [])
        bills = []
        for bill_data in bills_data:
            serializer = BillSerializer(data=bill_data)
            if serializer.is_valid():
                bills.append(serializer.save())
        created_counts['bills'] = len(bills)
        
        # Cash Drops
        cash_drops_data = validated_data.get('cash_drops', [])
        cash_drops = CashDrop.objects.bulk_create([
            CashDrop(**data) for data in cash_drops_data
        ])
        created_counts['cash_drops'] = len(cash_drops)
        
        # Store Sessions
        sessions_data = validated_data.get('store_sessions', [])
        sessions = StoreSession.objects.bulk_create([
            StoreSession(**data) for data in sessions_data
        ], ignore_conflicts=True)
        created_counts['store_sessions'] = len(sessions)
        
        # Cashier Shifts
        shifts_data = validated_data.get('cashier_shifts', [])
        shifts = CashierShift.objects.bulk_create([
            CashierShift(**data) for data in shifts_data
        ])
        created_counts['cashier_shifts'] = len(shifts)
        
        # Kitchen Orders
        kitchen_data = validated_data.get('kitchen_orders', [])
        kitchen_orders = KitchenOrder.objects.bulk_create([
            KitchenOrder(**data) for data in kitchen_data
        ])
        created_counts['kitchen_orders'] = len(kitchen_orders)
        
        # Bill Refunds
        refunds_data = validated_data.get('bill_refunds', [])
        refunds = BillRefund.objects.bulk_create([
            BillRefund(**data) for data in refunds_data
        ])
        created_counts['bill_refunds'] = len(refunds)
        
        # Inventory Movements
        inv_data = validated_data.get('inventory_movements', [])
        inv_movements = InventoryMovement.objects.bulk_create([
            InventoryMovement(**data) for data in inv_data
        ])
        created_counts['inventory_movements'] = len(inv_movements)
        
        return created_counts
