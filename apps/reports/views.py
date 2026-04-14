"""
Reports Views — Occupancy, revenue, tax, and analytics reports.
"""
import csv
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Q

from apps.core.mixins import OwnerManagerMixin
from apps.rooms.models import Room
from apps.reservations.models import Reservation
from apps.billing.models import Folio, Payment, TaxRecord, FolioCharge
from apps.billing.tax import get_monthly_tax_summary
from apps.guests.models import Guest


class ReportsDashboardView(OwnerManagerMixin, View):
    """Reports overview page."""

    def get(self, request):
        return render(request, 'reports/index.html')


class OccupancyReportView(OwnerManagerMixin, View):
    """Occupancy report — daily/monthly breakdown."""

    def get(self, request):
        today = date.today()
        days = int(request.GET.get('days', 30))
        start_date = today - timedelta(days=days)

        total_rooms = Room.active.count()
        daily_data = []

        for i in range(days + 1):
            d = start_date + timedelta(days=i)
            occupied = Reservation.active.filter(
                check_in_date__lte=d,
                check_out_date__gt=d,
                status__in=['checked_in', 'checked_out'],
            ).count()
            rate = round((occupied / total_rooms * 100), 1) if total_rooms > 0 else 0
            daily_data.append({'date': d, 'occupied': occupied, 'rate': rate})

        avg_occupancy = sum(d['rate'] for d in daily_data) / len(daily_data) if daily_data else 0

        context = {
            'daily_data': daily_data,
            'total_rooms': total_rooms,
            'avg_occupancy': round(avg_occupancy, 1),
            'days': days,
        }
        return render(request, 'reports/occupancy.html', context)


class RevenueReportView(OwnerManagerMixin, View):
    """Revenue report — by source, type, and time period."""

    def get(self, request):
        today = date.today()
        month_start = today.replace(day=1)

        # Monthly revenue by charge type
        revenue_by_type = FolioCharge.objects.filter(
            created_at__date__gte=month_start,
        ).values('charge_type').annotate(
            total=Sum('amount'),
            count=Count('id'),
        ).order_by('-total')

        # Monthly payments by method
        payments_by_method = Payment.objects.filter(
            created_at__date__gte=month_start,
        ).values('method').annotate(
            total=Sum('amount'),
            count=Count('id'),
        ).order_by('-total')

        # Total revenue
        total_revenue = Payment.objects.filter(
            created_at__date__gte=month_start,
        ).aggregate(total=Sum('amount'))['total'] or 0

        context = {
            'revenue_by_type': revenue_by_type,
            'payments_by_method': payments_by_method,
            'total_revenue': total_revenue,
            'month': today.strftime('%B %Y'),
        }
        return render(request, 'reports/revenue.html', context)


class TaxReportView(OwnerManagerMixin, View):
    """PB1 Tax report for monthly filing."""

    def get(self, request):
        today = date.today()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))

        summary = get_monthly_tax_summary(year, month)

        # Get all tax records for the period
        records = TaxRecord.objects.filter(
            period_year=year,
            period_month=month
        ).select_related('folio', 'folio__reservation', 'folio__reservation__guest')

        context = {
            'summary': summary,
            'records': records,
            'year': year,
            'month': month,
            'years': range(2024, today.year + 1),
            'months': range(1, 13),
        }
        return render(request, 'reports/tax_report.html', context)


class GuestReportView(OwnerManagerMixin, View):
    """Guest demographics report."""

    def get(self, request):
        # Nationality breakdown
        nationality_data = Guest.active.values('nationality').annotate(
            count=Count('id')
        ).order_by('-count')[:20]

        # Foreign vs domestic
        total_guests = Guest.active.count()
        foreign_guests = Guest.active.exclude(nationality='Indonesian').count()

        context = {
            'nationality_data': nationality_data,
            'total_guests': total_guests,
            'foreign_guests': foreign_guests,
            'domestic_guests': total_guests - foreign_guests,
        }
        return render(request, 'reports/guests.html', context)


class ExportCSVView(OwnerManagerMixin, View):
    """Export report data as CSV."""

    def get(self, request, report_type):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="mantahotel_{report_type}_{date.today()}.csv"'
        writer = csv.writer(response)

        if report_type == 'guests':
            writer.writerow(['Name', 'Phone', 'Email', 'Nationality', 'ID Type', 'ID Number', 'VIP', 'Total Stays'])
            for guest in Guest.active.all():
                writer.writerow([guest.full_name, guest.phone, guest.email, guest.nationality, guest.id_type, guest.id_number, guest.is_vip, guest.total_stays])

        elif report_type == 'foreign_guests':
            # APOA export for immigration
            writer.writerow(['Full Name', 'Nationality', 'Passport Number', 'Date of Birth', 'Gender', 'Country', 'Phone'])
            for guest in Guest.active.filter(id_type='passport').exclude(nationality='Indonesian'):
                writer.writerow([guest.full_name, guest.nationality, guest.id_number, guest.date_of_birth, guest.gender, guest.country, guest.phone])

        return response
