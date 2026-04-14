"""Reservation URLs."""
from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.ReservationListView.as_view(), name='list'),
    path('create/', views.ReservationCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.ReservationDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.ReservationEditView.as_view(), name='edit'),
    path('check-availability/', views.AvailabilityCheckView.as_view(), name='check_availability'),
    path('calendar/', views.ReservationCalendarView.as_view(), name='calendar'),
]
