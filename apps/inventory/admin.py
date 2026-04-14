"""Inventory Administration."""
from django.contrib import admin
from .models import InventoryCategory, InventoryItem, StockTransaction, Supplier


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name',)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_stock', 'min_stock_level', 'unit', 'unit_cost', 'is_low_stock')
    list_filter = ('category', 'supplier')
    search_fields = ('name', 'sku')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'transaction_type', 'quantity', 'unit_cost', 'created_at')
    list_filter = ('transaction_type',)
    date_hierarchy = 'created_at'
