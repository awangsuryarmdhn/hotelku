"""
Guest Views — CRUD, profiles, and stay history.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q

from apps.core.mixins import FrontDeskMixin
from .models import Guest
from .forms import GuestForm


class GuestListView(LoginRequiredMixin, View):
    """List all guests with search."""

    def get(self, request):
        guests = Guest.active.all()

        search = request.GET.get('q')
        if search:
            guests = guests.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(id_number__icontains=search)
            )

        vip_only = request.GET.get('vip')
        if vip_only:
            guests = guests.filter(is_vip=True)

        context = {
            'guests': guests[:50],
            'search_query': search or '',
            'total_guests': guests.count(),
        }

        if request.htmx:
            return render(request, 'guests/partials/guest_list.html', context)
        return render(request, 'guests/list.html', context)


class GuestCreateView(FrontDeskMixin, View):
    """Create a new guest profile."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request):
        form = GuestForm()
        return render(request, 'guests/form.html', {'form': form, 'title': 'Register New Guest'})

    def post(self, request):
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guest registered successfully.')
            if request.htmx:
                return render(request, 'guests/partials/guest_created.html', {'guest': form.instance})
            return redirect('guests:list')
        return render(request, 'guests/form.html', {'form': form, 'title': 'Register New Guest'})


class GuestEditView(FrontDeskMixin, View):
    """Edit guest profile."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']

    def get(self, request, pk):
        guest = get_object_or_404(Guest, pk=pk)
        form = GuestForm(instance=guest)
        return render(request, 'guests/form.html', {'form': form, 'title': f'Edit: {guest.full_name}', 'guest': guest})

    def post(self, request, pk):
        guest = get_object_or_404(Guest, pk=pk)
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            messages.success(request, f'Guest {guest.full_name} updated.')
            return redirect('guests:profile', pk=guest.pk)
        return render(request, 'guests/form.html', {'form': form, 'title': f'Edit: {guest.full_name}', 'guest': guest})


class GuestProfileView(LoginRequiredMixin, View):
    """View guest profile with stay history."""

    def get(self, request, pk):
        guest = get_object_or_404(Guest, pk=pk)
        reservations = guest.reservations.all().order_by('-check_in_date')[:10]
        context = {
            'guest': guest,
            'reservations': reservations,
        }
        return render(request, 'guests/profile.html', context)


class GuestSearchView(LoginRequiredMixin, View):
    """HTMX endpoint for live guest search (used in reservation forms)."""

    def get(self, request):
        query = request.GET.get('q', '')
        guests = []
        if len(query) >= 2:
            guests = Guest.active.filter(
                Q(full_name__icontains=query) |
                Q(phone__icontains=query) |
                Q(id_number__icontains=query)
            )[:10]
        return render(request, 'guests/partials/search_results.html', {'guests': guests})
