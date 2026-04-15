"""
Billing Views — Folio management, charges, payments, and invoices.
"""
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages

from apps.core.mixins import FrontDeskMixin
from .models import Folio, FolioCharge, Payment
from .forms import ChargeForm, PaymentForm


class FolioListView(LoginRequiredMixin, View):
    """List all folios."""

    def get(self, request):
        folios = Folio.active.select_related(
            'reservation', 'reservation__guest'
        ).all()

        status = request.GET.get('status')
        payment = request.GET.get('payment')

        if status:
            folios = folios.filter(status=status)
        if payment:
            folios = folios.filter(payment_status=payment)

        context = {'folios': folios[:50]}
        return render(request, 'billing/folio_list.html', context)


class FolioDetailView(LoginRequiredMixin, View):
    """View folio with all charges and payments."""

    def get(self, request, pk):
        folio = get_object_or_404(
            Folio.objects.select_related('reservation', 'reservation__guest'),
            pk=pk
        )
        charges = folio.charges.all()
        payments = folio.payments.all()
        charge_form = ChargeForm()
        payment_form = PaymentForm()

        context = {
            'folio': folio,
            'charges': charges,
            'payments': payments,
            'charge_form': charge_form,
            'payment_form': payment_form,
        }
        return render(request, 'billing/folio.html', context)


class AddChargeView(FrontDeskMixin, View):
    """Add a charge to a folio."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']
    
    def get(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)
        form = ChargeForm()
        context = {'form': form, 'folio': folio, 'title': 'Add Charge Item'}
        if request.htmx:
            return render(request, 'billing/partials/charge_modal.html', context)
        return redirect('billing:folio_detail', pk=folio.pk)

    def post(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)

        if folio.status == 'closed':
            messages.error(request, 'Cannot add charges to a closed folio.')
            return redirect('billing:folio_detail', pk=folio.pk)

        form = ChargeForm(request.POST)
        if form.is_valid():
            charge = form.save(commit=False)
            charge.folio = folio
            charge.posted_by = request.user
            charge.save()
            messages.success(request, f'Charge added: {charge.description}')

        if request.htmx:
            charges = folio.charges.all()
            return render(request, 'billing/partials/charge_list.html', {'folio': folio, 'charges': charges})
        return redirect('billing:folio_detail', pk=folio.pk)


class AddPaymentView(FrontDeskMixin, View):
    """Record a payment against a folio."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']
    
    def get(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)
        form = PaymentForm()
        context = {'form': form, 'folio': folio, 'title': 'Record Payment'}
        if request.htmx:
            return render(request, 'billing/partials/payment_modal.html', context)
        return redirect('billing:folio_detail', pk=folio.pk)

    def post(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.folio = folio
            payment.received_by = request.user
            payment.save()  # This auto-updates folio payment status
            messages.success(request, f'Payment received: Rp {payment.amount}')

        if request.htmx:
            payments = folio.payments.all()
            return render(request, 'billing/partials/payment_list.html', {'folio': folio, 'payments': payments})
        return redirect('billing:folio_detail', pk=folio.pk)


class InvoiceView(LoginRequiredMixin, View):
    """Generate printable invoice view."""

    def get(self, request, pk):
        folio = get_object_or_404(
            Folio.objects.select_related('reservation', 'reservation__guest'),
            pk=pk
        )
        charges = folio.charges.all()
        payments = folio.payments.all()

        context = {
            'folio': folio,
            'charges': charges,
            'payments': payments,
        }
        return render(request, 'billing/invoice.html', context)
