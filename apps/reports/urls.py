"""Reports URLs."""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsDashboardView.as_view(), name='index'),
    path('occupancy/', views.OccupancyReportView.as_view(), name='occupancy'),
    path('revenue/', views.RevenueReportView.as_view(), name='revenue'),
    path('tax/', views.TaxReportView.as_view(), name='tax'),
    path('guests/', views.GuestReportView.as_view(), name='guests'),
    path('export/<str:report_type>/', views.ExportCSVView.as_view(), name='export'),
]
