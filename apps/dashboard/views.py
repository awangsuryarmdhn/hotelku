"""
Dashboard Views — Main overview with KPIs and quick actions.
=============================================================
Shows today's occupancy, arrivals, departures, and revenue summary.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q
from django.shortcuts import render
from django.views import View

from apps.rooms.models import Room
from apps.reservations.models import Reservation
from apps.billing.models import Folio, Payment
from apps.housekeeping.models import HousekeepingTask


class DashboardView(LoginRequiredMixin, View):
    """Main dashboard with hotel KPIs and quick overview."""

    def get(self, request):
        today = date.today()

        # ── Room Statistics ──
        total_rooms = Room.active.count()
        occupied_rooms = Room.active.filter(status='occupied').count()
        available_rooms = Room.active.filter(status='available').count()
        dirty_rooms = Room.active.filter(status='dirty').count()
        maintenance_rooms = Room.active.filter(status='maintenance').count()
        occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0

        # ── Today's Activity ──
        todays_arrivals = Reservation.active.filter(
            check_in_date=today,
            status='confirmed'
        ).select_related('guest').count()

        todays_departures = Reservation.active.filter(
            check_out_date=today,
            status='checked_in'
        ).select_related('guest').count()

        todays_checkins = Reservation.active.filter(
            check_in_date=today,
            status='checked_in'
        ).count()

        # ── Revenue (This Month) ──
        month_start = today.replace(day=1)
        monthly_revenue = Payment.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=today,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        todays_revenue = Payment.objects.filter(
            created_at__date=today,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # ── Pending Housekeeping ──
        pending_tasks = HousekeepingTask.active.filter(
            status__in=['pending', 'in_progress']
        ).count()

        # ── Recent Reservations ──
        recent_reservations = Reservation.active.filter(
            status__in=['confirmed', 'checked_in']
        ).select_related('guest').order_by('-created_at')[:5]

        # ── Arrivals List ──
        arrivals = Reservation.active.filter(
            check_in_date=today,
            status='confirmed'
        ).select_related('guest')

        # ── Departures List ──
        departures = Reservation.active.filter(
            check_out_date=today,
            status='checked_in'
        ).select_related('guest')

        context = {
            'today': today,
            # Room stats
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'dirty_rooms': dirty_rooms,
            'maintenance_rooms': maintenance_rooms,
            'occupancy_rate': occupancy_rate,
            # Activity
            'todays_arrivals': todays_arrivals,
            'todays_departures': todays_departures,
            'todays_checkins': todays_checkins,
            # Revenue
            'monthly_revenue': monthly_revenue,
            'todays_revenue': todays_revenue,
            # Tasks
            'pending_tasks': pending_tasks,
            # Lists
            'recent_reservations': recent_reservations,
            'arrivals': arrivals,
            'departures': departures,
        }

        return render(request, 'dashboard/index.html', context)
