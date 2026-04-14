"""Guest Administration."""
from django.contrib import admin
from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'id_type', 'nationality', 'is_vip', 'total_stays')
    list_filter = ('id_type', 'nationality', 'is_vip')
    search_fields = ('full_name', 'email', 'phone', 'id_number')
