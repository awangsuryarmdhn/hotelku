"""
Accounts Models — Custom User model for MantaHotel.
====================================================
Extends Django's AbstractUser with hotel-specific fields.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for hotel staff.

    Inherits from Django's AbstractUser which provides:
    - username, email, password (hashed)
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login
    - Groups & Permissions (RBAC)

    We add hotel-specific fields below.
    """

    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
        ('housekeeping', 'Housekeeping'),
        ('pos_staff', 'POS Staff'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='receptionist',
        help_text='Primary role for this staff member'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Phone number (e.g., +62 812-3456-7890)'
    )
    avatar_url = models.URLField(
        blank=True,
        help_text='URL to profile picture'
    )

    class Meta:
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def display_name(self):
        """Return full name or username as fallback."""
        return self.get_full_name() or self.username

    @property
    def initials(self):
        """Return first letter of first and last name."""
        if self.first_name and self.last_name:
            return f'{self.first_name[0]}{self.last_name[0]}'.upper()
        return self.username[0].upper()
