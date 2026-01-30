from django.urls import path
from promotions.views import promotion_views, compiler_views, settings_views

app_name = 'promotion'

urlpatterns = [
    # Promotion Management
    path('', promotion_views.promotion_list, name='list'),
    path('create/', promotion_views.promotion_create, name='create'),
    path('<uuid:pk>/edit/', promotion_views.promotion_update, name='edit'),
    path('<uuid:pk>/delete/', promotion_views.promotion_delete, name='delete'),
    
    # Compiler & Sync Dashboard
    path('compiler/', compiler_views.compiler_dashboard, name='compiler_dashboard'),
    path('compiler/compile/<uuid:promotion_id>/', compiler_views.compile_promotion, name='compile_promotion'),
    path('compiler/compile-all/', compiler_views.compile_all_active, name='compile_all_active'),
    path('compiler/compile-store/<uuid:store_id>/', compiler_views.compile_for_store, name='compile_for_store'),
    path('compiler/compile-company/', compiler_views.compile_for_company, name='compile_for_company'),
    path('compiler/preview/<uuid:promotion_id>/', compiler_views.preview_compiled_json, name='preview_json'),
    # path('compiler/api-docs/', compiler_views.api_documentation, name='api_documentation'),
    
    # Sync Settings
    path('settings/', settings_views.sync_settings, name='sync_settings'),
    path('settings/preview-query/', settings_views.preview_sync_query, name='preview_sync_query'),
]
