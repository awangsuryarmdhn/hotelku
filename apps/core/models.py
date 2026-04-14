"""
Core Models — Base model that all other models inherit from.
================================================
Provides: UUID primary key, timestamps, soft delete.
Every table in MantaHotel gets these fields automatically.
"""
import uuid

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model for all MantaHotel models.

    Fields added automatically:
    - id: UUID primary key (no sequential IDs for security)
    - created_at: When the record was created
    - updated_at: When the record was last modified
    - deleted_at: Soft delete timestamp (null = active)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this record was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this record was last updated'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Soft delete timestamp. Null means active.'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Mark record as deleted without removing from database."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_active(self):
        """Check if record is not soft-deleted."""
        return self.deleted_at is None


class ActiveManager(models.Manager):
    """
    Custom manager that excludes soft-deleted records by default.
    Usage: MyModel.active.all() returns only non-deleted records.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
