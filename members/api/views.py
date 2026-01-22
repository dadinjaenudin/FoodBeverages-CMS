"""
Members API Views - Bidirectional Sync (HO ↔ Edge)
HO → Edge: Pull member data
Edge → HO: Register new member, update points/visits
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from members.models import Member, MemberTransaction
from .serializers import (
    MemberSerializer, MemberTransactionSerializer,
    MemberRegistrationSerializer, MemberUpdateSerializer
)


class MemberViewSet(viewsets.ModelViewSet):
    """
    Member master data - Bidirectional sync
    GET: Edge pulls member data (incremental)
    POST: Edge registers new member
    PATCH: Edge updates member (points, visits, spent)
    """
    queryset = Member.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MemberRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return MemberUpdateSerializer
        return MemberSerializer
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync members for specific company
        Query params: company_id, last_sync, phone (optional for lookup)
        """
        company_id = request.query_params.get('company_id')
        last_sync = request.query_params.get('last_sync')
        phone = request.query_params.get('phone')
        
        if not company_id:
            return Response(
                {'error': 'company_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(company_id=company_id)
        
        # Phone lookup for POS
        if phone:
            queryset = queryset.filter(phone=phone)
        
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register new member from Edge
        Edge sends member data, HO generates member_code
        """
        serializer = MemberRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            return Response(
                MemberSerializer(member).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_stats(self, request, pk=None):
        """
        Update member statistics from Edge (after purchase)
        Body: { points, point_balance, total_visits, total_spent, last_visit }
        """
        member = self.get_object()
        serializer = MemberUpdateSerializer(member, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def lookup(self, request):
        """
        Lookup member by phone or member_code (for POS)
        Body: { company_id, phone } or { company_id, member_code }
        """
        company_id = request.data.get('company_id')
        phone = request.data.get('phone')
        member_code = request.data.get('member_code')
        
        if not company_id:
            return Response(
                {'error': 'company_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(company_id=company_id)
        
        if phone:
            queryset = queryset.filter(phone=phone)
        elif member_code:
            queryset = queryset.filter(member_code=member_code)
        else:
            return Response(
                {'error': 'phone or member_code required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member = queryset.first()
        if not member:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(member)
        return Response(serializer.data)


class MemberTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Member transaction history - Read-only for Edge
    Edge pushes transactions to HO via separate endpoint
    """
    queryset = MemberTransaction.objects.select_related('member').all()
    serializer_class = MemberTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync member transactions
        Query params: member_id, last_sync
        """
        member_id = request.query_params.get('member_id')
        last_sync = request.query_params.get('last_sync')
        
        if not member_id:
            return Response(
                {'error': 'member_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(member_id=member_id)
        
        if last_sync:
            queryset = queryset.filter(created_at__gt=last_sync)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'last_sync': timezone.now().isoformat(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def create_transaction(self, request):
        """
        Create member transaction from Edge
        Body: { member_id, transaction_type, points, description, bill_id, created_by }
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Calculate balance_after
            member = Member.objects.get(id=request.data['member_id'])
            balance_after = member.point_balance + request.data['points']
            
            with transaction.atomic():
                txn = serializer.save(balance_after=balance_after)
                
                # Update member balance
                member.point_balance = balance_after
                if request.data['transaction_type'] == 'EARN':
                    member.points += request.data['points']
                member.save(update_fields=['point_balance', 'points'])
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
