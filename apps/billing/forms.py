"""Billing Forms."""
from django import forms
from .models import FolioCharge, Payment

INPUT_CSS = 'input input-bordered w-full'
SELECT_CSS = 'select select-bordered w-full'
TEXTAREA_CSS = 'textarea textarea-bordered w-full'


class ChargeForm(forms.ModelForm):
    """Form for adding charges to a folio."""

    class Meta:
        model = FolioCharge
        fields = ['charge_type', 'description', 'amount', 'quantity', 'is_taxable']
        widgets = {
            'charge_type': forms.Select(attrs={'class': SELECT_CSS}),
            'description': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Charge description'}),
            'amount': forms.NumberInput(attrs={'class': INPUT_CSS, 'placeholder': 'Amount in IDR'}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CSS, 'min': 1, 'value': 1}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments."""

    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': INPUT_CSS, 'placeholder': 'Payment amount in IDR'}),
            'method': forms.Select(attrs={'class': SELECT_CSS}),
            'reference': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Transaction reference'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2}),
        }
