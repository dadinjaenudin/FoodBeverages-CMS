from django.shortcuts import render
from django.utils import timezone
from .models import Bill, BillItem
from datetime import timedelta

def queue_display_view(request):
    """
    Display queue/serving numbers for orders
    Shows NOW SERVING and PREPARING sections
    """
    # Get orders from today
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # NOW SERVING: READY status orders (last 30 minutes)
    now_serving = BillItem.objects.filter(
        status='READY',
        prepared_at__gte=timezone.now() - timedelta(minutes=30),
        created_at__gte=today_start,
        is_void=False
    ).select_related('bill').order_by('prepared_at')[:10]
    
    # PREPARING: Orders in PREPARING status
    preparing = BillItem.objects.filter(
        status='PREPARING',
        created_at__gte=today_start,
        is_void=False
    ).select_related('bill').order_by('sent_to_kitchen_at')[:10]
    
    # Group by bill for compact display
    serving_orders = {}
    for item in now_serving:
        bill_num = item.bill_id
        if bill_num not in serving_orders:
            bill = Bill.objects.get(id=bill_num)
            serving_orders[bill_num] = {
                'bill_number': bill.bill_number.split('-')[-1] if '-' in bill.bill_number else bill.bill_number,
                'customer_name': bill.customer_name or 'Customer',
                'prepared_at': item.prepared_at,
                'items': []
            }
        serving_orders[bill_num]['items'].append({
            'product_name': item.product_name,
            'quantity': item.quantity
        })
    
    preparing_orders = {}
    for item in preparing:
        bill_num = item.bill_id
        if bill_num not in preparing_orders:
            bill = Bill.objects.get(id=bill_num)
            preparing_orders[bill_num] = {
                'bill_number': bill.bill_number.split('-')[-1] if '-' in bill.bill_number else bill.bill_number,
                'customer_name': bill.customer_name or 'Customer',
                'sent_at': item.sent_to_kitchen_at,
                'items': [],
                'is_ready': False
            }
        preparing_orders[bill_num]['items'].append({
            'product_name': item.product_name,
            'quantity': item.quantity
        })
    
    context = {
        'serving_orders': list(serving_orders.values())[:6],
        'preparing_orders': list(preparing_orders.values())[:9],
        'current_time': timezone.now(),
    }
    
    return render(request, 'transactions/queue_display.html', context)
