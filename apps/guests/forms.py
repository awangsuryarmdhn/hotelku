"""Guest Forms."""
from django import forms
from .models import Guest

INPUT_CSS = 'input input-bordered w-full'
SELECT_CSS = 'select select-bordered w-full'
TEXTAREA_CSS = 'textarea textarea-bordered w-full'


class GuestForm(forms.ModelForm):
    """Form for creating/editing guest profiles."""

    class Meta:
        model = Guest
        fields = [
            'full_name', 'email', 'phone', 'gender', 'date_of_birth',
            'id_type', 'id_number', 'address', 'city', 'country',
            'nationality', 'is_vip', 'notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Full name as on ID'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CSS, 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': '+62 812-xxxx-xxxx'}),
            'gender': forms.Select(attrs={'class': SELECT_CSS}),
            'date_of_birth': forms.DateInput(attrs={'class': INPUT_CSS, 'type': 'date'}),
            'id_type': forms.Select(attrs={'class': SELECT_CSS}),
            'id_number': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'KTP or Passport number'}),
            'address': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2}),
            'city': forms.TextInput(attrs={'class': INPUT_CSS}),
            'country': forms.TextInput(attrs={'class': INPUT_CSS}),
            'nationality': forms.TextInput(attrs={'class': INPUT_CSS}),
            'is_vip': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 3, 'placeholder': 'Special requests, preferences...'}),
        }
