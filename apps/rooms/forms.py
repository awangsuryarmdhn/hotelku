"""Room Forms."""
from django import forms
from .models import Room, RoomType


INPUT_CSS = 'input input-bordered w-full'
SELECT_CSS = 'select select-bordered w-full'
TEXTAREA_CSS = 'textarea textarea-bordered w-full'


class RoomForm(forms.ModelForm):
    """Form for creating/editing rooms."""

    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'floor', 'status', 'rate_override', 'notes']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'e.g., 101'}),
            'room_type': forms.Select(attrs={'class': SELECT_CSS}),
            'floor': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'status': forms.Select(attrs={'class': SELECT_CSS}),
            'rate_override': forms.NumberInput(attrs={'class': INPUT_CSS, 'placeholder': 'Leave blank for default rate'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 3}),
        }


class RoomTypeForm(forms.ModelForm):
    """Form for creating/editing room types."""

    class Meta:
        model = RoomType
        fields = ['name', 'description', 'base_rate', 'max_occupancy', 'amenities']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'e.g., Deluxe Room'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 3}),
            'base_rate': forms.NumberInput(attrs={'class': INPUT_CSS, 'placeholder': 'e.g., 1500000'}),
            'max_occupancy': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'amenities': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2, 'placeholder': 'AC, WiFi, TV, Minibar, Pool Access'}),
        }
