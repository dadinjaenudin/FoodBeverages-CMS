from django.urls import path
from .views import user_views

app_name = 'user'

urlpatterns = [
    path('', user_views.user_list, name='list'),
    path('create/', user_views.user_create, name='create'),
    path('<uuid:pk>/edit/', user_views.user_edit, name='edit'),
    path('<uuid:pk>/delete/', user_views.user_delete, name='delete'),
]
