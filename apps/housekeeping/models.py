"""
Housekeeping Models — Cleaning tasks and maintenance requests.
===============================================================
HousekeepingTask: Track room cleaning with Kanban-style status.
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, ActiveManager


class HousekeepingTask(BaseModel):
    """
    A cleaning or maintenance task for a specific room.

    Workflow: Dirty → In Progress → Clean → Inspected
    Auto-created when a guest checks out.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('inspected', 'Inspected'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    TYPE_CHOICES = [
        ('checkout_clean', 'Check-out Cleaning'),
        ('stayover_clean', 'Stayover Cleaning'),
        ('deep_clean', 'Deep Cleaning'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
    ]

    room = models.ForeignKey(
        'rooms.Room', on_delete=models.CASCADE,
        related_name='housekeeping_tasks',
        help_text='Room to be cleaned/maintained'
    )
    task_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='checkout_clean'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='normal'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='housekeeping_tasks',
        help_text='Staff member assigned to this task'
    )
    notes = models.TextField(blank=True, help_text='Task notes or issues found')
    completed_at = models.DateTimeField(
        null=True, blank=True,
        help_text='When the task was completed'
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Housekeeping Task'
        verbose_name_plural = 'Housekeeping Tasks'

    def __str__(self):
        return f'{self.get_task_type_display()} — Room {self.room.room_number}'
