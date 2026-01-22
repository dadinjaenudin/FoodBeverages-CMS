"""
Management Command: Expire Member Points
Run daily via Celery Beat or cron
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from datetime import timedelta
from members.models import Member, MemberTransaction


class Command(BaseCommand):
    help = 'Expire member points based on company policy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be expired without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        self.stdout.write(self.style.WARNING(
            f"Running member points expiry job for {today}"
        ))
        
        # Get all active companies with expiry policy
        from core.models import Company
        companies = Company.objects.filter(
            is_active=True,
            point_expiry_months__gt=0
        )
        
        total_expired = 0
        total_members = 0
        
        for company in companies:
            self.stdout.write(f"\nProcessing company: {company.name} ({company.code})")
            
            # Calculate expiry date
            expiry_months = company.point_expiry_months
            expiry_date = today - timedelta(days=expiry_months * 30)
            
            # Find members with points to expire
            members = Member.objects.filter(
                company_id=company.id,
                is_active=True,
                point_balance__gt=0
            )
            
            for member in members:
                # Get transactions older than expiry period that haven't been expired
                expired_transactions = MemberTransaction.objects.filter(
                    member=member,
                    transaction_type='EARN',
                    created_at__date__lte=expiry_date,
                    points__gt=0,
                    is_expired=False
                )
                
                member_expired_points = 0
                
                for txn in expired_transactions:
                    if dry_run:
                        self.stdout.write(
                            f"  [DRY RUN] Would expire {txn.points} points from {member.member_code} "
                            f"(transaction date: {txn.created_at.date()})"
                        )
                    else:
                        # Mark transaction as expired
                        txn.is_expired = True
                        txn.expired_at = timezone.now()
                        txn.save()
                        
                        # Create expiry transaction
                        MemberTransaction.objects.create(
                            member=member,
                            transaction_type='EXPIRED',
                            points=-txn.points,
                            balance_after=member.point_balance - txn.points,
                            description=f'Points expired (earned on {txn.created_at.date()})',
                            created_by=None  # System automated
                        )
                        
                        member_expired_points += txn.points
                
                if member_expired_points > 0:
                    if not dry_run:
                        # Update member balance
                        member.point_balance = F('point_balance') - member_expired_points
                        member.save(update_fields=['point_balance'])
                        member.refresh_from_db()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Expired {member_expired_points} points for {member.member_code} "
                            f"(new balance: {member.point_balance})"
                        )
                    )
                    
                    total_expired += member_expired_points
                    total_members += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Would have expired {total_expired} points for {total_members} members"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully expired {total_expired} points for {total_members} members"
                )
            )
