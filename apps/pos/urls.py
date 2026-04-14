"""POS URLs."""
from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.POSTerminalView.as_view(), name='terminal'),
    path('order/', views.POSCreateOrderView.as_view(), name='create_order'),
    path('menu/', views.POSMenuManageView.as_view(), name='menu_manage'),
]
