"""Front Desk URLs."""
from django.urls import path
from . import views

app_name = 'frontdesk'

urlpatterns = [
    path('', views.FrontDeskBoardView.as_view(), name='board'),
    path('checkin/<uuid:pk>/', views.CheckInView.as_view(), name='checkin'),
    path('checkout/<uuid:pk>/', views.CheckOutView.as_view(), name='checkout'),
    path('walkin/', views.WalkInView.as_view(), name='walkin'),
]
