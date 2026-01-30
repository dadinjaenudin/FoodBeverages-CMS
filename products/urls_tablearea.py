"""
Table Area URLs
"""
from django.urls import path
from products.views import tablearea_views
from products.views import enhanced_tablearea_views

app_name = 'tablearea'

urlpatterns = [
    path('', tablearea_views.tablearea_list, name='list'),
    path('enhanced/', enhanced_tablearea_views.enhanced_tablearea_list, name='enhanced_list'),
    path('dashboard/', enhanced_tablearea_views.tablearea_dashboard, name='dashboard'),
    path('floor-plan/', enhanced_tablearea_views.floor_plan_overview, name='floor_plan'),
    path('create/', tablearea_views.tablearea_create, name='create'),
    path('<uuid:pk>/edit/', tablearea_views.tablearea_update, name='edit'),
    path('<uuid:pk>/delete/', tablearea_views.tablearea_delete, name='delete'),
    path('<uuid:area_id>/layout/', enhanced_tablearea_views.area_table_layout, name='layout'),
    path('update-table-status/', enhanced_tablearea_views.update_table_status, name='update_table_status'),
    path('tables/create/', enhanced_tablearea_views.create_table, name='create_table'),
    path('tables/update/', enhanced_tablearea_views.update_table, name='update_table'),
    path('tables/delete/', enhanced_tablearea_views.delete_table, name='delete_table'),
]
