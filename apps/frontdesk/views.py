"""
Front Desk Views — Check-in, check-out, and walk-in operations.
=================================================================
The heart of daily hotel operations.
"""
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone

from apps.core.mixins import FrontDeskMixin
from apps.core.utils import generate_invoice_number
from apps.reservations.models import Reservation, ReservationRoom
from apps.rooms.models import Room
from apps.billing.models import Folio, FolioCharge
from apps.housekeeping.models import HousekeepingTask
from apps.guests.models import Guest


class FrontDeskBoardView(FrontDeskMixin, View):
    """
    Front desk operations board.
    Shows today's arrivals, departures, and in-house guests.
    """
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request):
        today = date.today()

        arrivals = Reservation.active.filter(
            check_in_date=today,
            status='confirmed'
        ).select_related('guest').prefetch_related('reservation_rooms__room')

        departures = Reservation.active.filter(
            check_out_date=today,
            status='checked_in'
        ).select_related('guest').prefetch_related('reservation_rooms__room')

        in_house = Reservation.active.filter(
            status='checked_in'
        ).select_related('guest').prefetch_related('reservation_rooms__room')

        rooms = Room.active.select_related('room_type').all()

        context = {
            'today': today,
            'arrivals': arrivals,
            'departures': departures,
            'in_house': in_house,
            'rooms': rooms,
        }
        return render(request, 'frontdesk/board.html', context)


class CheckInView(FrontDeskMixin, View):
    """Process guest check-in for a reservation."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request, pk):
        reservation = get_object_or_404(
            Reservation.objects.select_related('guest'),
            pk=pk
        )
        reservation_rooms = reservation.reservation_rooms.select_related('room', 'room__room_type')
        context = {
            'reservation': reservation,
            'reservation_rooms': reservation_rooms,
        }
        return render(request, 'frontdesk/checkin.html', context)

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)

        if reservation.status != 'confirmed':
            messages.error(request, 'This reservation cannot be checked in.')
            return redirect('frontdesk:board')

        # 1. Update reservation status
        reservation.status = 'checked_in'
        reservation.actual_check_in = timezone.now()
        reservation.save(update_fields=['status', 'actual_check_in', 'updated_at'])

        # 2. Set rooms to occupied
        for res_room in reservation.reservation_rooms.all():
            res_room.room.set_status('occupied')

        # 3. Create folio
        folio = Folio.objects.create(
            reservation=reservation,
            invoice_number=generate_invoice_number('INV'),
            status='open',
        )

        # 4. Add room charges to folio
        for res_room in reservation.reservation_rooms.all():
            for night in range(reservation.nights):
                FolioCharge.objects.create(
                    folio=folio,
                    charge_type='room',
                    description=f'Room {res_room.room.room_number} — Night {night + 1}',
                    amount=res_room.rate,
                    quantity=1,
                    is_taxable=True,
                    posted_by=request.user,
                )

        # 5. Update guest stay count
        reservation.guest.increment_stays()

        messages.success(request, f'Guest {reservation.guest.full_name} checked in successfully.')
        return redirect('frontdesk:board')


class CheckOutView(FrontDeskMixin, View):
    """Process guest check-out."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request, pk):
        reservation = get_object_or_404(
            Reservation.objects.select_related('guest'),
            pk=pk
        )
        folio = reservation.folio if hasattr(reservation, 'folio') else None
        reservation_rooms = reservation.reservation_rooms.select_related('room')

        context = {
            'reservation': reservation,
            'folio': folio,
            'reservation_rooms': reservation_rooms,
        }
        return render(request, 'frontdesk/checkout.html', context)

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)

        if reservation.status != 'checked_in':
            messages.error(request, 'This reservation is not checked in.')
            return redirect('frontdesk:board')

        # 1. Update reservation status
        reservation.status = 'checked_out'
        reservation.actual_check_out = timezone.now()
        reservation.save(update_fields=['status', 'actual_check_out', 'updated_at'])

        # 2. Close folio
        if hasattr(reservation, 'folio'):
            folio = reservation.folio
            folio.status = 'closed'
            folio.save(update_fields=['status', 'updated_at'])

            # Create tax record
            from apps.billing.tax import calculate_folio_tax
            calculate_folio_tax(folio)

        # 3. Set rooms to dirty & create housekeeping tasks
        for res_room in reservation.reservation_rooms.all():
            res_room.room.set_status('dirty')
            HousekeepingTask.objects.create(
                room=res_room.room,
                task_type='checkout_clean',
                status='pending',
                priority='normal',
            )

        messages.success(request, f'Guest {reservation.guest.full_name} checked out.')
        return redirect('frontdesk:board')


class WalkInView(FrontDeskMixin, View):
    """Handle walk-in guests — create reservation + check-in in one step."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request):
        available_rooms = Room.active.filter(status='available').select_related('room_type')
        context = {
            'available_rooms': available_rooms,
            'today': date.today(),
        }
        return render(request, 'frontdesk/walkin.html', context)
