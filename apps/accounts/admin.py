"""
Accounts Admin — Register User model with Django admin.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin view for User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'groups')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Hotel Info', {'fields': ('role', 'phone', 'avatar_url')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Hotel Info', {'fields': ('role', 'phone')}),
    )
