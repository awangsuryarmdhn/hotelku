"""Reservation Administration."""
from django.contrib import admin
from .models import Reservation, ReservationRoom


class ReservationRoomInline(admin.TabularInline):
    model = ReservationRoom
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_code', 'guest', 'check_in_date', 'check_out_date', 'status', 'source')
    list_filter = ('status', 'source', 'check_in_date')
    search_fields = ('guest__full_name',)
    inlines = [ReservationRoomInline]
    date_hierarchy = 'check_in_date'
