"""Room URLs."""
from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.RoomListView.as_view(), name='list'),
    path('grid/', views.RoomGridView.as_view(), name='grid'),
    path('create/', views.RoomCreateView.as_view(), name='create'),
    path('<uuid:pk>/edit/', views.RoomEditView.as_view(), name='edit'),
    path('<uuid:pk>/status/', views.RoomStatusUpdateView.as_view(), name='status_update'),
    path('types/', views.RoomTypeListView.as_view(), name='types'),
    path('types/create/', views.RoomTypeCreateView.as_view(), name='type_create'),
]
