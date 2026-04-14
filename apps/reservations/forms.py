"""Reservation Forms."""
from django import forms
from .models import Reservation

INPUT_CSS = 'input input-bordered w-full'
SELECT_CSS = 'select select-bordered w-full'
TEXTAREA_CSS = 'textarea textarea-bordered w-full'


class ReservationForm(forms.ModelForm):
    """Form for creating/editing reservations."""

    class Meta:
        model = Reservation
        fields = [
            'guest', 'check_in_date', 'check_out_date',
            'num_guests', 'source', 'status', 'special_requests', 'notes',
        ]
        widgets = {
            'guest': forms.Select(attrs={'class': SELECT_CSS}),
            'check_in_date': forms.DateInput(attrs={'class': INPUT_CSS, 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': INPUT_CSS, 'type': 'date'}),
            'num_guests': forms.NumberInput(attrs={'class': INPUT_CSS, 'min': 1}),
            'source': forms.Select(attrs={'class': SELECT_CSS}),
            'status': forms.Select(attrs={'class': SELECT_CSS}),
            'special_requests': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2}),
        }
