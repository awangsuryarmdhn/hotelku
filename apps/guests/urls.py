"""Guest URLs."""
from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    path('', views.GuestListView.as_view(), name='list'),
    path('create/', views.GuestCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.GuestProfileView.as_view(), name='profile'),
    path('<uuid:pk>/edit/', views.GuestEditView.as_view(), name='edit'),
    path('search/', views.GuestSearchView.as_view(), name='search'),
]
