"""
POS Models — Menu items and orders for restaurant/bar/spa.
===========================================================
MenuCategory & MenuItem: What's available to order.
PosOrder & PosOrderItem: Orders placed, can be charged to room folio.
"""
from decimal import Decimal

from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, ActiveManager


class MenuCategory(BaseModel):
    """Category for POS menu items (e.g., Food, Drinks, Spa, Laundry)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0, help_text='Display order')

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Menu Category'
        verbose_name_plural = 'Menu Categories'

    def __str__(self):
        return self.name


class MenuItem(BaseModel):
    """A single item on the POS menu with pricing."""
    category = models.ForeignKey(
        MenuCategory, on_delete=models.PROTECT,
        related_name='items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Price in IDR'
    )
    is_available = models.BooleanField(default=True)
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Linked inventory item for auto stock deduction'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'

    def __str__(self):
        return f'{self.name} — Rp {self.price}'


class PosOrder(BaseModel):
    """
    A POS order from restaurant, bar, spa, etc.
    Can be charged to a room folio or paid directly.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('room_charge', 'Charge to Room'),
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('qris', 'QRIS'),
    ]

    order_number = models.CharField(
        max_length=20, unique=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='open'
    )
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES, default='room_charge'
    )
    # If charged to room
    room = models.ForeignKey(
        'rooms.Room', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pos_orders',
        help_text='Room to charge (if room_charge payment)'
    )
    folio = models.ForeignKey(
        'billing.Folio', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pos_orders',
        help_text='Folio to charge (auto-linked from room)'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'POS Order'
        verbose_name_plural = 'POS Orders'

    def __str__(self):
        return f'Order {self.order_number}'

    @property
    def total(self):
        """Calculate order total."""
        total = self.items.aggregate(
            total=models.Sum(
                models.F('price') * models.F('quantity'),
                output_field=models.DecimalField()
            )
        )['total']
        return total or Decimal('0')


class PosOrderItem(BaseModel):
    """A single item on a POS order."""
    order = models.ForeignKey(
        PosOrder, on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.PROTECT
    )
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text='Price at time of order (in case menu price changes)'
    )
    notes = models.TextField(blank=True, help_text='Special instructions')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity}x {self.menu_item.name}'

    @property
    def total(self):
        return self.price * self.quantity
