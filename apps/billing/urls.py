"""Billing URLs."""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.FolioListView.as_view(), name='list'),
    path('<uuid:pk>/', views.FolioDetailView.as_view(), name='folio_detail'),
    path('<uuid:pk>/charge/', views.AddChargeView.as_view(), name='add_charge'),
    path('<uuid:pk>/payment/', views.AddPaymentView.as_view(), name='add_payment'),
    path('<uuid:pk>/invoice/', views.InvoiceView.as_view(), name='invoice'),
]
