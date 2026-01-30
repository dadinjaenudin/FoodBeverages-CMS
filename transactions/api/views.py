"""
Transactions API Views - Edge → HO Push
Receive transaction data from Edge servers (write-only endpoints)
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from transactions.models import (
    Bill, BillItem, Payment, BillPromotion, CashDrop,
    StoreSession, CashierShift, KitchenOrder, BillRefund, InventoryMovement
)
from .serializers import (
    BillSerializer, CashDropSerializer, StoreSessionSerializer,
    CashierShiftSerializer, KitchenOrderSerializer, BillRefundSerializer,
    InventoryMovementSerializer, BulkTransactionSerializer
)


@extend_schema(tags=['Transactions'])
class BillPushViewSet(viewsets.ViewSet):
    """
    Receive bills from Edge (create-only)
    POST /api/v1/transactions/bills/push/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Push Single Bill",
        description="Receive a single completed bill from Edge server",
        responses={201: None},
        request=BillSerializer
    )
    @action(detail=False, methods=['post'])
    def push(self, request):
        """
        Push single bill with items, payments, promotions
        Body: { bill_data with nested items/payments/promotions }
        """
        serializer = BillSerializer(data=request.data)
        if serializer.is_valid():
            bill = serializer.save()
            return Response(
                {'success': True, 'bill_id': str(bill.id)},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Push Bulk Bills",
        description="Receive multiple bills from Edge server in one request",
        responses={201: None}
    )
    @action(detail=False, methods=['post'])
    def push_bulk(self, request):
        """
        Push multiple bills in one request
        Body: { bills: [...] }
        """
        bills_data = request.data.get('bills', [])
        created_bills = []
        errors = []
        
        for idx, bill_data in enumerate(bills_data):
            serializer = BillSerializer(data=bill_data)
            if serializer.is_valid():
                bill = serializer.save()
                created_bills.append(str(bill.id))
            else:
                errors.append({
                    'index': idx,
                    'errors': serializer.errors
                })
        
        return Response({
            'success': len(errors) == 0,
            'created': len(created_bills),
            'failed': len(errors),
            'bill_ids': created_bills,
            'errors': errors
        }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_207_MULTI_STATUS)


@extend_schema(tags=['Transactions'])
class CashDropPushViewSet(viewsets.ViewSet):
    """Receive cash drops from Edge"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Push Cash Drop",
        description="Receive a cash drop record from Edge server",
        request=CashDropSerializer
    )
    @action(detail=False, methods=['post'])
    def push(self, request):
        """Push single cash drop"""
        serializer = CashDropSerializer(data=request.data)
        if serializer.is_valid():
            cash_drop = serializer.save()
            return Response(
                {'success': True, 'id': str(cash_drop.id)},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Push Bulk Cash Drops",
        description="Receive multiple cash drop records from Edge server"
    )
    @action(detail=False, methods=['post'])
    def push_bulk(self, request):
        """Push multiple cash drops"""
        cash_drops_data = request.data.get('cash_drops', [])
        cash_drops = CashDrop.objects.bulk_create([
            CashDrop(**data) for data in cash_drops_data
        ])
        return Response({
            'success': True,
            'created': len(cash_drops)
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Transactions'])
class StoreSessionPushViewSet(viewsets.ViewSet):
    """Receive EOD sessions from Edge"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Push Store Session (EOD)",
        description="Receive End of Day session data from Edge server",
        request=StoreSessionSerializer
    )
    @action(detail=False, methods=['post'])
    def push(self, request):
        """Push store session (EOD)"""
        serializer = StoreSessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response(
                {'success': True, 'id': str(session.id)},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Transactions'])
class CashierShiftPushViewSet(viewsets.ViewSet):
    """Receive cashier shifts from Edge"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Push Cashier Shift",
        description="Receive cashier shift data from Edge server",
        request=CashierShiftSerializer
    )
    @action(detail=False, methods=['post'])
    def push(self, request):
        """Push cashier shift"""
        serializer = CashierShiftSerializer(data=request.data)
        if serializer.is_valid():
            shift = serializer.save()
            return Response(
                {'success': True, 'id': str(shift.id)},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Transactions'])
class InventoryMovementPushViewSet(viewsets.ViewSet):
    """Receive inventory movements from Edge"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Push Bulk Inventory Movements",
        description="Receive stock movements (deductions) from Edge server"
    )
    @action(detail=False, methods=['post'])
    def push_bulk(self, request):
        """Push multiple inventory movements"""
        movements_data = request.data.get('movements', [])
        movements = InventoryMovement.objects.bulk_create([
            InventoryMovement(**data) for data in movements_data
        ])
        return Response({
            'success': True,
            'created': len(movements)
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Transactions'], summary="Bulk Push All Data", description="Receive mixed transaction data in one request")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_push(request):
    """
    Bulk push endpoint - all transaction types in one request
    Useful for Edge to sync multiple record types at once
    
    Body: {
      bills: [...],
      cash_drops: [...],
      store_sessions: [...],
      cashier_shifts: [...],
      kitchen_orders: [...],
      bill_refunds: [...],
      inventory_movements: [...]
    }
    """
    serializer = BulkTransactionSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            created_counts = serializer.save()
        
        return Response({
            'success': True,
            'created': created_counts,
            'message': 'Bulk transaction push successful'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
