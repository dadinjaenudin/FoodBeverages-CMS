from django.urls import path
from .views import auth_views
from .views import global_filter_views

app_name = 'auth'

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('set-global-filter/', global_filter_views.set_global_filter, name='set_global_filter'),
]
