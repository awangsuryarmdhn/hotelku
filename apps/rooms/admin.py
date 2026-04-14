"""Room Administration — Django Admin configuration."""
from django.contrib import admin
from .models import RoomType, Room


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_rate', 'max_occupancy', 'created_at')
    search_fields = ('name',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'floor', 'status', 'nightly_rate')
    list_filter = ('status', 'room_type', 'floor')
    search_fields = ('room_number',)
    list_editable = ('status',)
