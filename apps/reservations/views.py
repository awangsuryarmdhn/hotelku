"""
Reservation Views — Booking CRUD, calendar, and availability check.
"""
from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q

from apps.core.mixins import FrontDeskMixin
from .models import Reservation, ReservationRoom
from .forms import ReservationForm
from apps.rooms.models import Room


class ReservationListView(LoginRequiredMixin, View):
    """List all reservations with filters."""

    def get(self, request):
        reservations = Reservation.active.select_related('guest').all()

        # Filters
        status = request.GET.get('status')
        source = request.GET.get('source')
        date_from = request.GET.get('from')
        date_to = request.GET.get('to')

        if status:
            reservations = reservations.filter(status=status)
        if source:
            reservations = reservations.filter(source=source)
        if date_from:
            reservations = reservations.filter(check_in_date__gte=date_from)
        if date_to:
            reservations = reservations.filter(check_in_date__lte=date_to)

        context = {
            'reservations': reservations[:100],
            'total': reservations.count(),
            'status_choices': Reservation.STATUS_CHOICES,
            'source_choices': Reservation.SOURCE_CHOICES,
        }

        if request.htmx:
            return render(request, 'reservations/partials/reservation_list.html', context)
        return render(request, 'reservations/list.html', context)


class ReservationCreateView(FrontDeskMixin, View):
    """Create a new reservation."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request):
        form = ReservationForm()
        available_rooms = Room.active.filter(status='available').select_related('room_type')
        context = {'form': form, 'title': 'New Reservation', 'available_rooms': available_rooms}
        return render(request, 'reservations/form.html', context)

    def post(self, request):
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.created_by = request.user
            reservation.save()

            # Assign rooms — fetch all in one query to avoid N+1
            room_ids = request.POST.getlist('room_ids')
            rooms_by_id = {
                str(r.pk): r
                for r in Room.objects.filter(pk__in=room_ids)
            }
            for room_id in room_ids:
                room = rooms_by_id.get(room_id)
                if room:
                    ReservationRoom.objects.create(
                        reservation=reservation,
                        room=room,
                        rate=room.nightly_rate
                    )

            messages.success(request, f'Reservation {reservation.reservation_code} created.')
            return redirect('reservations:detail', pk=reservation.pk)

        available_rooms = Room.active.filter(status='available').select_related('room_type')
        return render(request, 'reservations/form.html', {'form': form, 'title': 'New Reservation', 'available_rooms': available_rooms})


class ReservationDetailView(LoginRequiredMixin, View):
    """View reservation details."""

    def get(self, request, pk):
        reservation = get_object_or_404(
            Reservation.objects.select_related('guest', 'created_by'),
            pk=pk
        )
        reservation_rooms = reservation.reservation_rooms.select_related('room', 'room__room_type')
        context = {
            'reservation': reservation,
            'reservation_rooms': reservation_rooms,
        }
        return render(request, 'reservations/detail.html', context)


class ReservationEditView(FrontDeskMixin, View):
    """Edit a reservation."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        form = ReservationForm(instance=reservation)
        available_rooms = Room.active.filter(
            Q(status='available') |
            Q(id__in=reservation.rooms.values_list('id', flat=True))
        ).select_related('room_type')
        context = {
            'form': form,
            'title': f'Edit {reservation.reservation_code}',
            'reservation': reservation,
            'available_rooms': available_rooms,
        }
        return render(request, 'reservations/form.html', context)

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, f'Reservation {reservation.reservation_code} updated.')
            return redirect('reservations:detail', pk=reservation.pk)
        return render(request, 'reservations/form.html', {'form': form, 'title': f'Edit {reservation.reservation_code}'})


class AvailabilityCheckView(LoginRequiredMixin, View):
    """HTMX endpoint to check room availability for date range."""

    def get(self, request):
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')

        if not check_in or not check_out:
            return render(request, 'reservations/partials/availability.html', {'rooms': []})

        # Find rooms that are NOT booked for the given date range
        booked_room_ids = ReservationRoom.objects.filter(
            reservation__check_in_date__lt=check_out,
            reservation__check_out_date__gt=check_in,
            reservation__status__in=['confirmed', 'checked_in'],
        ).values_list('room_id', flat=True)

        available_rooms = Room.active.exclude(
            id__in=booked_room_ids
        ).exclude(
            status__in=['maintenance', 'out_of_order']
        ).select_related('room_type')

        return render(request, 'reservations/partials/availability.html', {
            'rooms': available_rooms,
            'check_in': check_in,
            'check_out': check_out,
        })


class ReservationCalendarView(LoginRequiredMixin, View):
    """Calendar view of reservations."""

    def get(self, request):
        today = date.today()
        # Show 14 days by default
        start_date = today - timedelta(days=1)
        end_date = today + timedelta(days=13)

        reservations = Reservation.active.filter(
            check_out_date__gte=start_date,
            check_in_date__lte=end_date,
            status__in=['confirmed', 'checked_in']
        ).select_related('guest').prefetch_related('reservation_rooms__room')

        dates = [start_date + timedelta(days=i) for i in range(15)]
        rooms = Room.active.select_related('room_type').all()

        context = {
            'dates': dates,
            'rooms': rooms,
            'reservations': reservations,
            'today': today,
        }
        return render(request, 'reservations/calendar.html', context)
