"""
Room Models — Room types and individual rooms.
================================================
RoomType: Categories like Standard, Deluxe, Suite, Villa
Room: Individual rooms with number, floor, status, and pricing
"""
from django.db import models
from apps.core.models import BaseModel, ActiveManager


class RoomType(BaseModel):
    """
    Room category/type (e.g., Standard, Deluxe, Suite, Villa, Bungalow).
    Each room type has a base rate and list of amenities.
    """
    name = models.CharField(max_length=100, help_text='e.g., Deluxe, Suite, Villa')
    description = models.TextField(blank=True, help_text='Description of this room type')
    base_rate = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Base nightly rate in IDR (e.g., 1500000)'
    )
    max_occupancy = models.IntegerField(default=2, help_text='Maximum number of guests')
    amenities = models.TextField(
        blank=True,
        help_text='Comma-separated amenities (e.g., AC, WiFi, TV, Minibar, Pool Access)'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['base_rate']
        verbose_name = 'Room Type'
        verbose_name_plural = 'Room Types'

    def __str__(self):
        return self.name

    @property
    def amenities_list(self):
        """Return amenities as a list."""
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(',')]


class Room(BaseModel):
    """
    Individual hotel room.
    Tracks room number, floor, current status, and pricing.
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('dirty', 'Dirty'),
        ('maintenance', 'Maintenance'),
        ('out_of_order', 'Out of Order'),
    ]

    room_number = models.CharField(
        max_length=10, unique=True,
        help_text='Room number (e.g., 101, 201A)'
    )
    room_type = models.ForeignKey(
        RoomType, on_delete=models.PROTECT,
        related_name='rooms',
        help_text='Which type of room this is'
    )
    floor = models.IntegerField(default=1, help_text='Floor number')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='available',
        help_text='Current room status'
    )
    rate_override = models.DecimalField(
        max_digits=12, decimal_places=0,
        null=True, blank=True,
        help_text='Override nightly rate (leave blank to use room type base rate)'
    )
    notes = models.TextField(blank=True, help_text='Internal notes about this room')

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['floor', 'room_number']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return f'Room {self.room_number} ({self.room_type.name})'

    @property
    def nightly_rate(self):
        """Return effective nightly rate (override or base rate)."""
        if self.rate_override:
            return self.rate_override
        return self.room_type.base_rate

    @property
    def is_available(self):
        """Check if room can be booked."""
        return self.status == 'available'

    def set_status(self, new_status):
        """Update room status."""
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
