"""Inventory URLs."""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='list'),
    path('create/', views.InventoryCreateView.as_view(), name='create'),
    path('<uuid:pk>/transaction/', views.StockTransactionView.as_view(), name='transaction'),
    path('<uuid:pk>/log/', views.StockLogView.as_view(), name='log'),
]
