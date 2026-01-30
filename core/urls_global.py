from django.urls import path
from .views import global_filter_views

app_name = 'global'

urlpatterns = [
    path('set-filter/', global_filter_views.set_global_filter, name='set_filter'),
]
