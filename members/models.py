"""
Member & Loyalty Program Models
- Member (company-wide with auto-generated code)
- MemberTransaction (earn/redeem/topup/payment/refund/adjustment/expired)
- Points & Balance tracking with full audit trail
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import Company, User


class Member(models.Model):
    """
    Member - Company-wide loyalty program
    Member code auto-generated: MB-{COMPANY_CODE}-{YYYYMM}-{XXXX}
    Example: MB-YGY-202601-0001
    """
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='members')
    member_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Auto-generated: MB-COMPANYCODE-YYYYMM-XXXX"
    )
    card_number = models.CharField(max_length=50, blank=True, help_text="Physical card number")
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, db_index=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Membership
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    joined_date = models.DateField(default=timezone.now)
    expire_date = models.DateField(null=True, blank=True)
    
    # Points & Balance
    points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Loyalty points balance"
    )
    point_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Monetary balance (from redeemed points or top-up)"
    )
    
    # Statistics (updated by Edge, synced back to HO)
    total_visits = models.IntegerField(default=0, help_text="Total number of visits")
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount spent"
    )
    last_visit = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='registered_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'member'
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'member_code']),
            models.Index(fields=['company', 'phone']),
            models.Index(fields=['tier', 'is_active']),
            models.Index(fields=['company', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.member_code} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate member_code if not exists"""
        if not self.member_code:
            # Generate: MB-{COMPANY_CODE}-{YYYYMM}-{XXXX}
            now = timezone.now()
            year_month = now.strftime('%Y%m')
            company_code = self.company.code
            
            # Get last member code for this company and month
            last_member = Member.objects.filter(
                company=self.company,
                member_code__startswith=f'MB-{company_code}-{year_month}-'
            ).order_by('-member_code').first()
            
            if last_member:
                # Extract sequence number and increment
                last_seq = int(last_member.member_code.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.member_code = f'MB-{company_code}-{year_month}-{new_seq:04d}'
        
        super().save(*args, **kwargs)
    
    def get_point_expiry_date(self):
        """Calculate point expiry date based on company/brand policy"""
        from dateutil.relativedelta import relativedelta
        expiry_months = self.company.get_point_expiry_months()
        if expiry_months == 0:
            return None  # Never expire
        return self.joined_date + relativedelta(months=expiry_months)


class MemberTransaction(models.Model):
    """
    Member Transaction - Points & Balance tracking with full audit trail
    All point/balance changes must go through this model
    """
    TRANSACTION_TYPE_CHOICES = [
        ('earn', 'Earn Points'),
        ('redeem', 'Redeem Points'),
        ('topup', 'Balance Top-up'),
        ('payment', 'Payment using Balance'),
        ('refund', 'Refund'),
        ('adjustment', 'Manual Adjustment'),
        ('expired', 'Points Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='transactions')
    bill_id = models.UUIDField(null=True, blank=True, help_text="Reference to Bill (if applicable)")
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # Points tracking
    points_change = models.IntegerField(
        default=0,
        help_text="Points change (+earn, -redeem/expired)"
    )
    points_before = models.IntegerField(default=0)
    points_after = models.IntegerField(default=0)
    
    # Balance tracking
    balance_change = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Balance change (+topup/refund, -payment)"
    )
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Audit trail
    reference = models.CharField(max_length=200, blank=True, help_text="External reference")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='member_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'member_transaction'
        verbose_name = 'Member Transaction'
        verbose_name_plural = 'Member Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
            models.Index(fields=['bill_id']),
        ]
    
    def __str__(self):
        return f"{self.member.member_code} - {self.get_transaction_type_display()} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        """
        Validate and update member balance atomically
        IMPORTANT: Always use this to create transactions, not direct Member.save()
        """
        if not self.pk:  # New transaction
            # Lock member row for update (prevent race condition)
            from django.db import transaction as db_transaction
            with db_transaction.atomic():
                member = Member.objects.select_for_update().get(pk=self.member.pk)
                
                # Set before values
                self.points_before = member.points
                self.balance_before = member.point_balance
                
                # Calculate after values
                self.points_after = self.points_before + self.points_change
                self.balance_after = self.balance_before + self.balance_change
                
                # Validate
                if self.points_after < 0:
                    raise ValueError(f"Insufficient points. Current: {self.points_before}, Required: {-self.points_change}")
                if self.balance_after < 0:
                    raise ValueError(f"Insufficient balance. Current: {self.balance_before}, Required: {-self.balance_change}")
                
                # Update member
                member.points = self.points_after
                member.point_balance = self.balance_after
                member.save(update_fields=['points', 'point_balance', 'updated_at'])
                
                # Save transaction
                super().save(*args, **kwargs)
        else:
            # Update existing transaction (should be rare)
            super().save(*args, **kwargs)
    
    @classmethod
    def earn_points(cls, member, amount, bill_id=None, created_by=None, notes=''):
        """
        Earn points from purchase
        Formula: points = amount * company.points_per_currency
        """
        points_to_earn = int(amount * float(member.company.points_per_currency))
        return cls.objects.create(
            member=member,
            bill_id=bill_id,
            transaction_type='earn',
            points_change=points_to_earn,
            reference=f'Bill {bill_id}' if bill_id else '',
            notes=notes or f'Earned {points_to_earn} points from purchase of {amount}',
            created_by=created_by
        )
    
    @classmethod
    def redeem_points(cls, member, points, balance_amount, created_by, notes=''):
        """
        Redeem points to balance
        Example: 500 points → 50,000 balance
        """
        if member.points < points:
            raise ValueError(f"Insufficient points. Current: {member.points}, Required: {points}")
        
        return cls.objects.create(
            member=member,
            transaction_type='redeem',
            points_change=-points,
            balance_change=balance_amount,
            reference=f'Redeemed {points} points',
            notes=notes or f'Redeemed {points} points for {balance_amount} balance',
            created_by=created_by
        )
    
    @classmethod
    def topup_balance(cls, member, amount, created_by, reference='', notes=''):
        """
        Top-up member balance via cash/transfer
        """
        return cls.objects.create(
            member=member,
            transaction_type='topup',
            balance_change=amount,
            reference=reference or f'Balance top-up {amount}',
            notes=notes or f'Balance top-up of {amount}',
            created_by=created_by
        )
    
    @classmethod
    def pay_with_balance(cls, member, amount, bill_id, created_by, notes=''):
        """
        Pay bill using member balance
        """
        if member.point_balance < amount:
            raise ValueError(f"Insufficient balance. Current: {member.point_balance}, Required: {amount}")
        
        return cls.objects.create(
            member=member,
            bill_id=bill_id,
            transaction_type='payment',
            balance_change=-amount,
            reference=f'Bill {bill_id}',
            notes=notes or f'Payment of {amount} using balance',
            created_by=created_by
        )
    
    @classmethod
    def expire_points(cls, member, points, created_by, notes=''):
        """
        Expire old points (called by management command)
        """
        if points > member.points:
            points = member.points  # Cap at current points
        
        if points > 0:
            return cls.objects.create(
                member=member,
                transaction_type='expired',
                points_change=-points,
                reference='Auto point expiry',
                notes=notes or f'{points} points expired automatically',
                created_by=created_by
            )
        return None
