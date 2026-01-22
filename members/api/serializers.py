"""
Members API Serializers - For HO ↔ Edge Bidirectional Sync
"""
from rest_framework import serializers
from members.models import Member, MemberTransaction


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['id', 'member_code', 'created_at', 'updated_at']


class MemberTransactionSerializer(serializers.ModelSerializer):
    member_code = serializers.CharField(source='member.member_code', read_only=True)
    
    class Meta:
        model = MemberTransaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MemberRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new member (from Edge)"""
    class Meta:
        model = Member
        fields = [
            'company_id', 'name', 'email', 'phone', 'birth_date',
            'gender', 'address', 'city', 'province', 'postal_code',
            'tier', 'created_by'
        ]
    
    def create(self, validated_data):
        # Auto-generate member_code at HO
        from core.models import Company
        from django.utils import timezone
        
        company_id = validated_data['company_id']
        company = Company.objects.get(id=company_id)
        
        # Generate member code: MB-COMPANYCODE-YYYYMM-XXXX
        now = timezone.now()
        year_month = now.strftime('%Y%m')
        
        # Get last sequence for this month
        prefix = f'MB-{company.code}-{year_month}-'
        last_member = Member.objects.filter(
            company_id=company_id,
            member_code__startswith=prefix
        ).order_by('-member_code').first()
        
        if last_member:
            last_seq = int(last_member.member_code.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        validated_data['member_code'] = f'{prefix}{new_seq:04d}'
        validated_data['joined_date'] = now.date()
        validated_data['points'] = 0
        validated_data['point_balance'] = 0
        validated_data['total_visits'] = 0
        validated_data['total_spent'] = 0
        
        return super().create(validated_data)


class MemberUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating member from Edge (points, visits, spent)"""
    class Meta:
        model = Member
        fields = [
            'id', 'member_code', 'tier', 'points', 'point_balance',
            'total_visits', 'total_spent', 'last_visit', 'updated_at'
        ]
        read_only_fields = ['member_code', 'updated_at']
