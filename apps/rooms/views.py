"""
Room Views — CRUD, visual grid, and status management.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from apps.core.mixins import FrontDeskMixin
from .models import Room, RoomType
from .forms import RoomForm, RoomTypeForm


class RoomListView(LoginRequiredMixin, View):
    """List all rooms with filters."""

    def get(self, request):
        rooms = Room.active.select_related('room_type').all()

        # Filters
        status = request.GET.get('status')
        room_type = request.GET.get('type')
        floor = request.GET.get('floor')

        if status:
            rooms = rooms.filter(status=status)
        if room_type:
            rooms = rooms.filter(room_type_id=room_type)
        if floor:
            rooms = rooms.filter(floor=floor)

        room_types = RoomType.active.all()
        floors = Room.active.values_list('floor', flat=True).distinct().order_by('floor')

        context = {
            'rooms': rooms,
            'room_types': room_types,
            'floors': floors,
            'current_status': status,
            'current_type': room_type,
            'current_floor': floor,
        }

        if request.htmx:
            return render(request, 'rooms/partials/room_list.html', context)
        return render(request, 'rooms/list.html', context)


class RoomGridView(LoginRequiredMixin, View):
    """Visual floor-by-floor room grid."""

    def get(self, request):
        rooms = Room.active.select_related('room_type').all()
        floors = Room.active.values_list('floor', flat=True).distinct().order_by('floor')

        rooms_by_floor = {}
        for floor in floors:
            rooms_by_floor[floor] = rooms.filter(floor=floor)

        context = {
            'rooms_by_floor': rooms_by_floor,
            'floors': floors,
        }
        return render(request, 'rooms/grid.html', context)


class RoomCreateView(FrontDeskMixin, View):
    """Create a new room."""
    allowed_roles = ['Owner', 'Manager']

    def get(self, request):
        form = RoomForm()
        return render(request, 'rooms/form.html', {'form': form, 'title': 'Add New Room'})

    def post(self, request):
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created successfully.')
            return redirect('rooms:list')
        return render(request, 'rooms/form.html', {'form': form, 'title': 'Add New Room'})


class RoomEditView(FrontDeskMixin, View):
    """Edit an existing room."""
    allowed_roles = ['Owner', 'Manager']

    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        form = RoomForm(instance=room)
        return render(request, 'rooms/form.html', {'form': form, 'title': f'Edit Room {room.room_number}', 'room': room})

    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f'Room {room.room_number} updated.')
            return redirect('rooms:list')
        return render(request, 'rooms/form.html', {'form': form, 'title': f'Edit Room {room.room_number}', 'room': room})


class RoomStatusUpdateView(FrontDeskMixin, View):
    """Quick status update via HTMX."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist', 'Housekeeping']

    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Room.STATUS_CHOICES):
            room.set_status(new_status)
            messages.success(request, f'Kamar {room.room_number} → {room.get_status_display()}')
        if request.htmx:
            return render(request, 'rooms/partials/room_card.html', {'room': room})
        return redirect('rooms:list')


class RoomTypeListView(FrontDeskMixin, View):
    """Manage room types."""
    allowed_roles = ['Owner', 'Manager']

    def get(self, request):
        room_types = RoomType.active.annotate(room_count=models.Count('rooms'))
        return render(request, 'rooms/types.html', {'room_types': room_types})


class RoomTypeCreateView(FrontDeskMixin, View):
    """Create a room type."""
    allowed_roles = ['Owner', 'Manager']

    def get(self, request):
        form = RoomTypeForm()
        return render(request, 'rooms/type_form.html', {'form': form, 'title': 'Add Room Type'})

    def post(self, request):
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room type created.')
            return redirect('rooms:types')
        return render(request, 'rooms/type_form.html', {'form': form, 'title': 'Add Room Type'})
