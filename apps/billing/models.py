"""
Billing Models — Folios, charges, payments, and tax records.
=============================================================
Folio: Running tab for a guest stay.
FolioCharge: Individual line items on the folio.
Payment: Payment records against a folio.
TaxRecord: PB1 tax tracking for compliance.
"""
from decimal import Decimal

from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, ActiveManager


class Folio(BaseModel):
    """
    Guest billing folio — a running tab of all charges during a stay.
    One folio per reservation. Created at check-in, closed at check-out.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ]

    reservation = models.OneToOneField(
        'reservations.Reservation',
        on_delete=models.PROTECT,
        related_name='folio',
        help_text='The reservation this folio belongs to'
    )
    invoice_number = models.CharField(
        max_length=30, unique=True, blank=True,
        help_text='Auto-generated invoice number (e.g., INV/2026/04/0001)'
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='open'
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid'
    )
    notes = models.TextField(blank=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Folio'
        verbose_name_plural = 'Folios'

    def __str__(self):
        return f'Folio {self.invoice_number} — {self.reservation.guest.full_name}'

    @property
    def subtotal(self):
        """Total of all charges before tax and service."""
        total = self.charges.aggregate(total=models.Sum('amount'))['total']
        return total or Decimal('0')

    @property
    def tax_amount(self):
        """PB1 hotel tax (10% on taxable charges)."""
        taxable = self.charges.filter(is_taxable=True).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        rate = Decimal(str(settings.HOTEL_TAX_RATE)) / Decimal('100')
        return taxable * rate

    @property
    def service_charge_amount(self):
        """Service charge on total."""
        rate = Decimal(str(settings.HOTEL_SERVICE_CHARGE)) / Decimal('100')
        return self.subtotal * rate

    @property
    def grand_total(self):
        """Total including tax and service charge."""
        return self.subtotal + self.tax_amount + self.service_charge_amount

    @property
    def total_paid(self):
        """Sum of all payments received."""
        total = self.payments.aggregate(total=models.Sum('amount'))['total']
        return total or Decimal('0')

    @property
    def balance_due(self):
        """Remaining balance to be paid."""
        return self.grand_total - self.total_paid

    def update_payment_status(self):
        """Update payment status based on payments received."""
        if self.total_paid >= self.grand_total:
            self.payment_status = 'paid'
        elif self.total_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'
        self.save(update_fields=['payment_status', 'updated_at'])


class FolioCharge(BaseModel):
    """
    A single charge on a guest folio.
    Can be room charge, F&B, minibar, laundry, spa, transport, etc.
    """
    CHARGE_TYPE_CHOICES = [
        ('room', 'Room Charge'),
        ('fnb', 'Food & Beverage'),
        ('minibar', 'Minibar'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa'),
        ('transport', 'Transport'),
        ('telephone', 'Telephone'),
        ('other', 'Other'),
    ]

    folio = models.ForeignKey(
        Folio, on_delete=models.CASCADE,
        related_name='charges',
        help_text='Which folio this charge belongs to'
    )
    charge_type = models.CharField(
        max_length=20, choices=CHARGE_TYPE_CHOICES, default='room'
    )
    description = models.CharField(
        max_length=200,
        help_text='Description of the charge (e.g., "Room 101 — Night 1")'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Charge amount in IDR'
    )
    quantity = models.IntegerField(
        default=1, help_text='Quantity (e.g., number of nights)'
    )
    is_taxable = models.BooleanField(
        default=True,
        help_text='Whether PB1 tax applies to this charge'
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Staff member who posted this charge'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Folio Charge'
        verbose_name_plural = 'Folio Charges'

    def __str__(self):
        return f'{self.description} — {self.amount}'

    @property
    def total(self):
        """Amount × Quantity."""
        return self.amount * self.quantity


class Payment(BaseModel):
    """
    Payment received against a folio.
    Supports multiple payment methods common in Indonesian hotels.
    """
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('qris', 'QRIS'),
        ('ota_collect', 'OTA Collected'),
        ('other', 'Other'),
    ]

    folio = models.ForeignKey(
        Folio, on_delete=models.CASCADE,
        related_name='payments',
        help_text='Which folio this payment applies to'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Payment amount in IDR'
    )
    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default='cash'
    )
    reference = models.CharField(
        max_length=100, blank=True,
        help_text='Transaction reference (card last 4, transfer ref, etc.)'
    )
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Staff member who received this payment'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'{self.get_method_display()} — Rp {self.amount}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update folio payment status after saving a payment
        self.folio.update_payment_status()


class TaxRecord(BaseModel):
    """
    PB1 tax records for government reporting.
    Auto-created when a folio is closed.
    """
    folio = models.OneToOneField(
        Folio, on_delete=models.CASCADE,
        related_name='tax_record'
    )
    taxable_amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Total taxable amount'
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text='Tax rate applied (e.g., 10.00)'
    )
    tax_amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Calculated tax amount'
    )
    service_charge_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        help_text='Service charge amount'
    )
    period_month = models.IntegerField(help_text='Tax period month (1-12)')
    period_year = models.IntegerField(help_text='Tax period year')

    class Meta:
        ordering = ['-period_year', '-period_month']
        verbose_name = 'Tax Record'
        verbose_name_plural = 'Tax Records'

    def __str__(self):
        return f'Tax — {self.folio.invoice_number}'
