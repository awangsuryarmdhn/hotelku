"""
Housekeeping Views — Kanban board and task management.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone

from apps.core.mixins import HousekeepingMixin
from .models import HousekeepingTask
from apps.rooms.models import Room


class HousekeepingBoardView(HousekeepingMixin, View):
    """Kanban board showing all housekeeping tasks by status."""
    allowed_roles = ['Owner', 'Manager', 'Housekeeping']

    def get(self, request):
        pending = HousekeepingTask.active.filter(status='pending').select_related('room', 'assigned_to')
        in_progress = HousekeepingTask.active.filter(status='in_progress').select_related('room', 'assigned_to')
        completed = HousekeepingTask.active.filter(status='completed').select_related('room', 'assigned_to')
        inspected = HousekeepingTask.active.filter(status='inspected').select_related('room', 'assigned_to')

        # Staff who can be assigned
        from apps.accounts.models import User
        housekeeping_staff = User.objects.filter(role='housekeeping', is_active=True)

        context = {
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'inspected': inspected,
            'housekeeping_staff': housekeeping_staff,
        }
        return render(request, 'housekeeping/board.html', context)


class HousekeepingUpdateView(HousekeepingMixin, View):
    """Update task status via HTMX."""
    allowed_roles = ['Owner', 'Manager', 'Housekeeping']

    def post(self, request, pk):
        task = get_object_or_404(HousekeepingTask, pk=pk)
        new_status = request.POST.get('status')

        if new_status in dict(HousekeepingTask.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()

            # If inspected, set room to available
            if new_status == 'inspected':
                task.room.set_status('available')
                messages.success(request, f'Room {task.room.room_number} is now available.')

        if request.htmx:
            return render(request, 'housekeeping/partials/task_card.html', {'task': task})
        return redirect('housekeeping:board')


class HousekeepingAssignView(HousekeepingMixin, View):
    """Assign a staff member to a task."""
    allowed_roles = ['Owner', 'Manager']

    def post(self, request, pk):
        task = get_object_or_404(HousekeepingTask, pk=pk)
        staff_id = request.POST.get('staff_id')

        if staff_id:
            from apps.accounts.models import User
            staff = get_object_or_404(User, pk=staff_id)
            task.assigned_to = staff
            task.save(update_fields=['assigned_to', 'updated_at'])
            messages.success(request, f'Task assigned to {staff.display_name}.')

        if request.htmx:
            return render(request, 'housekeeping/partials/task_card.html', {'task': task})
        return redirect('housekeeping:board')
