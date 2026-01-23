"""
Analytics URLs - Reporting UI (HTML Pages)
"""
from django.urls import path
from . import report_views

app_name = 'analytics'

urlpatterns = [
    # UI Reports (HTML)
    path('sales-report/', report_views.sales_report_dashboard, name='sales-report'),
    path('product-performance/', report_views.product_performance_report, name='product-performance'),
    path('hourly-sales/', report_views.hourly_sales_report, name='hourly-sales'),
]
