"""
PB1 Tax Calculation Engine — Indonesian Hotel Tax.
===================================================
Calculates Pajak Hotel (PB1) at 10% on room and applicable charges.
Generates monthly tax summaries for filing.
"""
from decimal import Decimal
from datetime import date

from django.conf import settings
from django.db.models import Sum

from apps.billing.models import TaxRecord, Folio


def calculate_folio_tax(folio):
    """
    Calculate and record PB1 tax for a closed folio.

    Args:
        folio: Folio instance (should be closed)

    Returns:
        TaxRecord instance
    """
    today = date.today()
    tax_rate = Decimal(str(settings.HOTEL_TAX_RATE))

    taxable_amount = folio.charges.filter(
        is_taxable=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    tax_amount = taxable_amount * (tax_rate / Decimal('100'))
    service_amount = folio.service_charge_amount

    tax_record, created = TaxRecord.objects.update_or_create(
        folio=folio,
        defaults={
            'taxable_amount': taxable_amount,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'service_charge_amount': service_amount,
            'period_month': today.month,
            'period_year': today.year,
        }
    )
    return tax_record


def get_monthly_tax_summary(year, month):
    """
    Get PB1 tax summary for a specific month.
    Used for monthly tax filing with local tax office.

    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)

    Returns:
        Dictionary with tax summary data
    """
    records = TaxRecord.objects.filter(
        period_year=year,
        period_month=month
    )

    summary = records.aggregate(
        total_taxable=Sum('taxable_amount'),
        total_tax=Sum('tax_amount'),
        total_service=Sum('service_charge_amount'),
    )

    return {
        'period': f'{year}-{month:02d}',
        'total_invoices': records.count(),
        'total_taxable_amount': summary['total_taxable'] or 0,
        'total_tax_collected': summary['total_tax'] or 0,
        'total_service_charge': summary['total_service'] or 0,
        'tax_rate': settings.HOTEL_TAX_RATE,
    }
