"""
Core Utilities — Helper functions used throughout MantaHotel.
=============================================================
Currency formatting, date helpers, ID generators.
"""
from datetime import date, timedelta
from decimal import Decimal


def format_idr(amount):
    """
    Format a number as Indonesian Rupiah.

    Examples:
        format_idr(1500000) → 'Rp 1.500.000'
        format_idr(75000.50) → 'Rp 75.001'
    """
    if amount is None:
        return 'Rp 0'

    amount = Decimal(str(amount))
    # Round to nearest whole number (no cents in IDR)
    amount = int(amount.quantize(Decimal('1')))

    # Format with dots as thousand separator (Indonesian style)
    formatted = f'{amount:,.0f}'.replace(',', '.')
    return f'Rp {formatted}'


def generate_invoice_number(prefix='INV'):
    """
    Generate a sequential invoice number in format: INV/2026/04/0001

    Args:
        prefix: String prefix (INV, RCV, etc.)

    Returns:
        String in format PREFIX/YYYY/MM/NNNN
    """
    today = date.today()
    from apps.billing.models import Folio  # Import here to avoid circular imports

    # Count existing invoices this month
    count = Folio.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
    ).count() + 1

    return f'{prefix}/{today.year}/{today.month:02d}/{count:04d}'


def date_range(start_date, end_date):
    """
    Generate a list of dates between start and end (inclusive).

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        List of date objects
    """
    days = (end_date - start_date).days + 1
    return [start_date + timedelta(days=i) for i in range(days)]


def calculate_nights(check_in, check_out):
    """
    Calculate number of nights between two dates.

    Args:
        check_in: Check-in date
        check_out: Check-out date

    Returns:
        Integer number of nights
    """
    if not check_in or not check_out:
        return 0
    delta = check_out - check_in
    return max(0, delta.days)
