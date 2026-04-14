"""
Reservation Models — Bookings and room assignments.
=====================================================
Reservation: The booking record with dates, guest, and status.
ReservationRoom: Links reservations to specific rooms (many-to-many).
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, ActiveManager
from apps.core.utils import calculate_nights


class Reservation(BaseModel):
    """
    A hotel reservation/booking.

    Tracks the guest, dates, source, status, and room assignments.
    """
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('tentative', 'Tentative'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    SOURCE_CHOICES = [
        ('direct', 'Direct / Walk-in'),
        ('phone', 'Phone'),
        ('website', 'Website'),
        ('booking_com', 'Booking.com'),
        ('agoda', 'Agoda'),
        ('traveloka', 'Traveloka'),
        ('tiket_com', 'Tiket.com'),
        ('expedia', 'Expedia'),
        ('airbnb', 'Airbnb'),
        ('other', 'Other OTA'),
    ]

    # Guest & Booking Info
    guest = models.ForeignKey(
        'guests.Guest', on_delete=models.PROTECT,
        related_name='reservations',
        help_text='The guest making the reservation'
    )
    check_in_date = models.DateField(help_text='Expected check-in date')
    check_out_date = models.DateField(help_text='Expected check-out date')
    num_guests = models.IntegerField(default=1, help_text='Number of guests')

    # Status & Source
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='confirmed'
    )
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default='direct',
        help_text='How this booking was made'
    )

    # Rooms assigned to this reservation
    rooms = models.ManyToManyField(
        'rooms.Room',
        through='ReservationRoom',
        related_name='reservations',
        help_text='Rooms assigned to this reservation'
    )

    # Notes & Tracking
    special_requests = models.TextField(
        blank=True, help_text='Guest special requests'
    )
    notes = models.TextField(blank=True, help_text='Internal notes')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_reservations',
        help_text='Staff member who created this booking'
    )

    # Actual timestamps
    actual_check_in = models.DateTimeField(
        null=True, blank=True,
        help_text='Actual check-in timestamp'
    )
    actual_check_out = models.DateTimeField(
        null=True, blank=True,
        help_text='Actual check-out timestamp'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['-check_in_date']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def __str__(self):
        return f'RES-{str(self.id)[:8].upper()} | {self.guest.full_name}'

    @property
    def nights(self):
        """Number of nights in this stay."""
        return calculate_nights(self.check_in_date, self.check_out_date)

    @property
    def reservation_code(self):
        """Short reservation code for display."""
        return f'RES-{str(self.id)[:8].upper()}'

    @property
    def total_room_charge(self):
        """Calculate total room charge for the entire stay."""
        total = 0
        for res_room in self.reservation_rooms.all():
            total += res_room.rate * self.nights
        return total


class ReservationRoom(BaseModel):
    """
    Links a reservation to a specific room with a rate.
    Allows multiple rooms per reservation & custom rate per room.
    """
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE,
        related_name='reservation_rooms'
    )
    room = models.ForeignKey(
        'rooms.Room', on_delete=models.PROTECT,
        related_name='reservation_rooms'
    )
    rate = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Nightly rate for this room in this reservation (IDR)'
    )

    class Meta:
        unique_together = ['reservation', 'room']
        verbose_name = 'Reservation Room'
        verbose_name_plural = 'Reservation Rooms'

    def __str__(self):
        return f'{self.reservation.reservation_code} → Room {self.room.room_number}'
