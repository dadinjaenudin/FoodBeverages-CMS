"""
Analytics API URLs - JSON Endpoints for Analytics Data
"""
from django.urls import path
from . import api_views

app_name = 'analytics_api'

urlpatterns = [
    # API Endpoints (JSON)
    path('daily-sales/', api_views.daily_sales_report, name='daily-sales'),
    path('product-sales/', api_views.product_sales_report, name='product-sales'),
    path('promotion-performance/', api_views.promotion_performance_report, name='promotion-performance'),
    path('member-analytics/', api_views.member_analytics_report, name='member-analytics'),
    path('inventory-cogs/', api_views.inventory_cogs_report, name='inventory-cogs'),
    path('cashier-performance/', api_views.cashier_performance_report, name='cashier-performance'),
    path('payment-methods/', api_views.payment_method_report, name='payment-methods'),
]
