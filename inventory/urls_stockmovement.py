from django.urls import path
from inventory.views import stockmovement_views

app_name = 'stockmovement'

urlpatterns = [
    path('', stockmovement_views.stockmovement_list, name='list'),
]
