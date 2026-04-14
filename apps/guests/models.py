"""
Guest Models — Guest profiles with ID, contact, and preferences.
=================================================================
Stores KTP (Indonesian ID) or passport for both local and foreign guests.
Supports APOA export for immigration compliance.
"""
from django.db import models
from apps.core.models import BaseModel, ActiveManager


class Guest(BaseModel):
    """
    Hotel guest profile.
    Stores personal info, ID documents, contact details, and preferences.
    """
    ID_TYPE_CHOICES = [
        ('ktp', 'KTP (Indonesian ID)'),
        ('passport', 'Passport'),
        ('sim', 'SIM (Driving License)'),
        ('other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # Personal Information
    full_name = models.CharField(max_length=200, help_text='Full name as on ID')
    email = models.EmailField(blank=True, help_text='Email address')
    phone = models.CharField(max_length=20, help_text='Phone number')
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)

    # Identification
    id_type = models.CharField(
        max_length=20, choices=ID_TYPE_CHOICES, default='ktp',
        help_text='Type of identification document'
    )
    id_number = models.CharField(
        max_length=50, help_text='KTP number, passport number, etc.'
    )

    # Address
    address = models.TextField(blank=True, help_text='Full address')
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(
        max_length=100, default='Indonesia',
        help_text='Country of origin (for APOA reporting)'
    )
    nationality = models.CharField(
        max_length=100, default='Indonesian',
        help_text='Nationality (for immigration compliance)'
    )

    # Preferences
    is_vip = models.BooleanField(default=False, help_text='VIP guest flag')
    notes = models.TextField(
        blank=True,
        help_text='Special requests, preferences, dietary needs, etc.'
    )
    total_stays = models.IntegerField(
        default=0, help_text='Number of times this guest has stayed'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'

    def __str__(self):
        return self.full_name

    @property
    def is_foreign(self):
        """Check if guest is a foreign national (for APOA reporting)."""
        return self.nationality.lower() != 'indonesian'

    @property
    def initials(self):
        """Get initials from full name."""
        parts = self.full_name.split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[-1][0]}'.upper()
        return self.full_name[0].upper()

    def increment_stays(self):
        """Increment the total stays counter."""
        self.total_stays += 1
        self.save(update_fields=['total_stays', 'updated_at'])
