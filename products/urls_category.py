"""
Category URLs
"""
from django.urls import path
from products.views import category_views

app_name = 'category'

urlpatterns = [
    path('', category_views.category_list, name='list'),
    path('create/', category_views.category_create, name='create'),
    path('<uuid:pk>/edit/', category_views.category_update, name='edit'),
    path('<uuid:pk>/delete/', category_views.category_delete, name='delete'),
]
