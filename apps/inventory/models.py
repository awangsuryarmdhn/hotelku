"""
Inventory Models — Stock items, categories, transactions, and suppliers.
=========================================================================
Track hotel consumables like food, beverages, amenities, linen, etc.
Auto-deduction when charges are posted from POS or minibar.
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, ActiveManager


class InventoryCategory(BaseModel):
    """Category for inventory items (e.g., Food, Beverages, Amenities, Linen)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'Inventory Category'
        verbose_name_plural = 'Inventory Categories'

    def __str__(self):
        return self.name


class Supplier(BaseModel):
    """Supplier/vendor for inventory items."""
    name = models.CharField(max_length=200, help_text='Supplier company name')
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.name


class InventoryItem(BaseModel):
    """
    Individual stock item.
    Tracks current quantity, minimum level for alerts, and unit cost.
    """
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('ltr', 'Liters'),
        ('box', 'Boxes'),
        ('pack', 'Packs'),
        ('btl', 'Bottles'),
        ('roll', 'Rolls'),
        ('set', 'Sets'),
    ]

    name = models.CharField(max_length=200, help_text='Item name')
    sku = models.CharField(
        max_length=50, unique=True, blank=True,
        help_text='Stock Keeping Unit code'
    )
    category = models.ForeignKey(
        InventoryCategory, on_delete=models.PROTECT,
        related_name='items'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='items'
    )
    unit = models.CharField(
        max_length=10, choices=UNIT_CHOICES, default='pcs'
    )
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        help_text='Cost per unit in IDR'
    )
    current_stock = models.IntegerField(
        default=0, help_text='Current stock quantity'
    )
    min_stock_level = models.IntegerField(
        default=10, help_text='Minimum stock level (triggers alert below this)'
    )
    notes = models.TextField(blank=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'

    def __str__(self):
        return f'{self.name} ({self.current_stock} {self.unit})'

    @property
    def is_low_stock(self):
        """Check if current stock is below minimum level."""
        return self.current_stock <= self.min_stock_level

    @property
    def stock_value(self):
        """Total value of current stock."""
        return self.current_stock * self.unit_cost

    def adjust_stock(self, quantity, transaction_type='out'):
        """
        Adjust stock quantity.

        Args:
            quantity: Number of units
            transaction_type: 'in' for purchase, 'out' for usage
        """
        if transaction_type == 'in':
            self.current_stock += quantity
        else:
            self.current_stock = max(0, self.current_stock - quantity)
        self.save(update_fields=['current_stock', 'updated_at'])


class StockTransaction(BaseModel):
    """
    Records every stock movement (in or out).
    Full audit trail of all inventory changes.
    """
    TYPE_CHOICES = [
        ('purchase', 'Purchase (In)'),
        ('usage', 'Usage (Out)'),
        ('adjustment', 'Adjustment'),
        ('waste', 'Waste/Spoilage'),
        ('return', 'Return to Supplier'),
    ]

    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES
    )
    quantity = models.IntegerField(help_text='Quantity moved')
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        help_text='Cost per unit at time of transaction'
    )
    reference = models.CharField(
        max_length=200, blank=True,
        help_text='Reference (e.g., PO number, room number, POS order)'
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'

    def __str__(self):
        direction = '+' if self.transaction_type == 'purchase' else '-'
        return f'{direction}{self.quantity} {self.item.name}'
