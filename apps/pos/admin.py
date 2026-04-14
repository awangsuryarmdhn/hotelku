"""POS Administration."""
from django.contrib import admin
from .models import MenuCategory, MenuItem, PosOrder, PosOrderItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    list_editable = ('sort_order',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    list_editable = ('is_available', 'price')


class PosOrderItemInline(admin.TabularInline):
    model = PosOrderItem
    extra = 0


@admin.register(PosOrder)
class PosOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'status', 'payment_type', 'room', 'created_at')
    list_filter = ('status', 'payment_type')
    inlines = [PosOrderItemInline]
