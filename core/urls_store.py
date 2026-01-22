"""
Store URL Configuration
"""

from django.urls import path
from core.views import store_views

app_name = 'store'

urlpatterns = [
    path('', store_views.store_list, name='list'),
    path('create/', store_views.store_create, name='create'),
    path('<uuid:pk>/edit/', store_views.store_update, name='edit'),
    path('<uuid:pk>/delete/', store_views.store_delete, name='delete'),
]
