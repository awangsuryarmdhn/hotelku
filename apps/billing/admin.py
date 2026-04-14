"""Billing Administration."""
from django.contrib import admin
from .models import Folio, FolioCharge, Payment, TaxRecord


class FolioChargeInline(admin.TabularInline):
    model = FolioCharge
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Folio)
class FolioAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'reservation', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('invoice_number', 'reservation__guest__full_name')
    inlines = [FolioChargeInline, PaymentInline]


@admin.register(TaxRecord)
class TaxRecordAdmin(admin.ModelAdmin):
    list_display = ('folio', 'taxable_amount', 'tax_rate', 'tax_amount', 'period_month', 'period_year')
    list_filter = ('period_year', 'period_month')
