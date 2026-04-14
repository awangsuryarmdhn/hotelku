"""POS Forms."""
from django import forms
from .models import MenuItem, MenuCategory

INPUT_CSS = 'input input-bordered w-full'
SELECT_CSS = 'select select-bordered w-full'
TEXTAREA_CSS = 'textarea textarea-bordered w-full'


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'is_available', 'inventory_item']
        widgets = {
            'category': forms.Select(attrs={'class': SELECT_CSS}),
            'name': forms.TextInput(attrs={'class': INPUT_CSS}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2}),
            'price': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'is_available': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'inventory_item': forms.Select(attrs={'class': SELECT_CSS}),
        }
