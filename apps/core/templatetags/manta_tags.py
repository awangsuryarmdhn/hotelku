"""
Custom Template Tags — Filters and tags for MantaHotel templates.
=================================================================
Usage in templates:
    {% load manta_tags %}
    {{ amount|idr }}         → Rp 1.500.000
    {{ room.status|status_badge }} → <span class="badge badge-success">Available</span>
"""
from django import template
from django.utils.safestring import mark_safe

from apps.core.utils import format_idr

register = template.Library()


@register.filter(name='idr')
def idr_filter(value):
    """
    Format a number as Indonesian Rupiah.
    Usage: {{ price|idr }} → Rp 1.500.000
    """
    return format_idr(value)


@register.filter(name='status_badge')
def status_badge(value):
    """
    Render a DaisyUI badge based on status value.
    Usage: {{ room.status|status_badge }}
    """
    badge_map = {
        # Room statuses
        'available': ('Available', 'badge-success'),
        'occupied': ('Occupied', 'badge-error'),
        'dirty': ('Dirty', 'badge-warning'),
        'maintenance': ('Maintenance', 'badge-info'),
        'out_of_order': ('Out of Order', 'badge-ghost'),
        # Reservation statuses
        'confirmed': ('Confirmed', 'badge-success'),
        'tentative': ('Tentative', 'badge-warning'),
        'checked_in': ('Checked In', 'badge-info'),
        'checked_out': ('Checked Out', 'badge-ghost'),
        'cancelled': ('Cancelled', 'badge-error'),
        'no_show': ('No Show', 'badge-error'),
        # Housekeeping
        'pending': ('Pending', 'badge-warning'),
        'in_progress': ('In Progress', 'badge-info'),
        'completed': ('Completed', 'badge-success'),
        'inspected': ('Inspected', 'badge-success'),
        # Payment
        'unpaid': ('Unpaid', 'badge-error'),
        'partial': ('Partial', 'badge-warning'),
        'paid': ('Paid', 'badge-success'),
    }

    label, css_class = badge_map.get(value, (str(value).title(), 'badge-ghost'))
    return mark_safe(f'<span class="badge {css_class} badge-sm gap-1">{label}</span>')


@register.filter(name='initials')
def initials_filter(value):
    """
    Get initials from a full name.
    Usage: {{ guest.name|initials }} → JD
    """
    if not value:
        return '?'
    parts = str(value).split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][0].upper()


@register.simple_tag
def active_nav(request, pattern):
    """
    Return 'active' CSS class if current URL matches the pattern.
    Usage: {% active_nav request 'rooms' %}
    """
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''
