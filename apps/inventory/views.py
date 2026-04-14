"""
Inventory Views — Stock management, transactions, and alerts.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages

from apps.core.mixins import OwnerManagerMixin
from .models import InventoryItem, InventoryCategory, StockTransaction, Supplier
from .forms import InventoryItemForm, StockTransactionForm


class InventoryListView(LoginRequiredMixin, View):
    """List all inventory items with stock levels."""

    def get(self, request):
        items = InventoryItem.active.select_related('category', 'supplier').all()

        category = request.GET.get('category')
        low_stock = request.GET.get('low_stock')

        if category:
            items = items.filter(category_id=category)
        if low_stock:
            items = [i for i in items if i.is_low_stock]

        categories = InventoryCategory.active.all()
        low_stock_count = sum(1 for i in InventoryItem.active.all() if i.is_low_stock)

        context = {
            'items': items,
            'categories': categories,
            'low_stock_count': low_stock_count,
        }

        if request.htmx:
            return render(request, 'inventory/partials/item_list.html', context)
        return render(request, 'inventory/list.html', context)


class InventoryCreateView(OwnerManagerMixin, View):
    """Add a new inventory item."""

    def get(self, request):
        form = InventoryItemForm()
        return render(request, 'inventory/form.html', {'form': form, 'title': 'Add Inventory Item'})

    def post(self, request):
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item added.')
            return redirect('inventory:list')
        return render(request, 'inventory/form.html', {'form': form, 'title': 'Add Inventory Item'})


class StockTransactionView(LoginRequiredMixin, View):
    """Record a stock transaction (purchase/usage)."""

    def post(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk)
        form = StockTransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.item = item
            transaction.recorded_by = request.user
            transaction.save()

            # Update stock levels
            if transaction.transaction_type == 'purchase':
                item.adjust_stock(transaction.quantity, 'in')
            else:
                item.adjust_stock(transaction.quantity, 'out')

            messages.success(request, f'Stock updated: {transaction}')

        return redirect('inventory:list')


class StockLogView(LoginRequiredMixin, View):
    """View stock transaction history for an item."""

    def get(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk)
        transactions = item.transactions.all()[:50]
        context = {'item': item, 'transactions': transactions}
        return render(request, 'inventory/stock_log.html', context)
