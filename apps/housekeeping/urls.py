"""Housekeeping URLs."""
from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('', views.HousekeepingBoardView.as_view(), name='board'),
    path('<uuid:pk>/update/', views.HousekeepingUpdateView.as_view(), name='update'),
    path('<uuid:pk>/assign/', views.HousekeepingAssignView.as_view(), name='assign'),
]
