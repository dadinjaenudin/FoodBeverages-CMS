"""
Transaction URLs - Queue Display
"""
from django.urls import path
from .views import queue_display_view

app_name = 'transactions'

urlpatterns = [
    path('queue/', queue_display_view, name='queue_display'),
]
