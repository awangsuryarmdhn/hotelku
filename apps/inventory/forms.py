"""Inventory Forms."""
from django import forms
from .models import InventoryItem, StockTransaction

INPUT_CSS = 'input input-bordered w-full'
SELECT_CSS = 'select select-bordered w-full'
TEXTAREA_CSS = 'textarea textarea-bordered w-full'


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'sku', 'category', 'supplier', 'unit', 'unit_cost', 'current_stock', 'min_stock_level', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CSS}),
            'sku': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'SKU-001'}),
            'category': forms.Select(attrs={'class': SELECT_CSS}),
            'supplier': forms.Select(attrs={'class': SELECT_CSS}),
            'unit': forms.Select(attrs={'class': SELECT_CSS}),
            'unit_cost': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'current_stock': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'min_stock_level': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2}),
        }


class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['transaction_type', 'quantity', 'unit_cost', 'reference', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': SELECT_CSS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CSS, 'min': 1}),
            'unit_cost': forms.NumberInput(attrs={'class': INPUT_CSS}),
            'reference': forms.TextInput(attrs={'class': INPUT_CSS}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CSS, 'rows': 2}),
        }
