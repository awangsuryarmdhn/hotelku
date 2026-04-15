"""
POS Views — Point of Sale terminal and order management.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages

from apps.core.mixins import POSMixin
from .models import MenuCategory, MenuItem, PosOrder, PosOrderItem
from apps.rooms.models import Room
from apps.billing.models import Folio, FolioCharge


class POSTerminalView(POSMixin, View):
    """POS terminal — touch-friendly order interface."""
    allowed_roles = ['Owner', 'Manager', 'POS Staff']

    def get(self, request):
        categories = MenuCategory.active.prefetch_related('items').all()
        occupied_rooms = Room.active.filter(status='occupied').select_related('room_type')

        context = {
            'categories': categories,
            'occupied_rooms': occupied_rooms,
        }
        return render(request, 'pos/terminal.html', context)


class POSCreateOrderView(POSMixin, View):
    """Create a new POS order."""
    allowed_roles = ['Owner', 'Manager', 'POS Staff']

    def post(self, request):
        payment_type = request.POST.get('payment_type', 'cash')
        room_id = request.POST.get('room_id')
        item_ids = request.POST.getlist('item_ids')
        quantities = request.POST.getlist('quantities')

        if not item_ids:
            messages.error(request, 'No items selected.')
            return redirect('pos:terminal')

        # Generate order number
        from datetime import date
        today = date.today()
        count = PosOrder.objects.filter(created_at__date=today).count() + 1
        order_number = f'POS-{today.strftime("%Y%m%d")}-{count:04d}'

        # Create order
        order = PosOrder.objects.create(
            order_number=order_number,
            status='completed',
            payment_type=payment_type,
            created_by=request.user,
        )

        # Link to room if room charge — use get_object_or_404 for safety
        if payment_type == 'room_charge' and room_id:
            room = get_object_or_404(Room, pk=room_id)
            order.room = room

            # Find active folio for this room
            from apps.reservations.models import ReservationRoom
            active_res_room = ReservationRoom.objects.filter(
                room=room,
                reservation__status='checked_in'
            ).select_related('reservation').first()

            if active_res_room and hasattr(active_res_room.reservation, 'folio'):
                order.folio = active_res_room.reservation.folio

            order.save()

        # Add items to order — fetch all menu items in one query to avoid N+1
        menu_items_by_id = {
            str(item.pk): item
            for item in MenuItem.objects.filter(pk__in=item_ids)
        }
        for i, item_id in enumerate(item_ids):
            if item_id:
                menu_item = menu_items_by_id.get(item_id)
                if not menu_item:
                    continue
                qty = int(quantities[i]) if i < len(quantities) else 1

                PosOrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=qty,
                    price=menu_item.price,
                )

                # Auto-deduct inventory if linked
                if menu_item.inventory_item:
                    menu_item.inventory_item.adjust_stock(qty, 'out')

        # Post to folio if room charge
        if order.folio:
            FolioCharge.objects.create(
                folio=order.folio,
                charge_type='fnb',
                description=f'POS Order {order.order_number}',
                amount=order.total,
                quantity=1,
                is_taxable=True,
                posted_by=request.user,
            )

        messages.success(request, f'Order {order.order_number} completed — Rp {order.total}')
        return redirect('pos:terminal')


class POSMenuManageView(POSMixin, View):
    """Manage POS menu items and categories."""
    allowed_roles = ['Owner', 'Manager']

    def get(self, request):
        categories = MenuCategory.active.prefetch_related('items').all()
        return render(request, 'pos/menu_manage.html', {'categories': categories})
