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
        # Status kamar
        'available': ('Tersedia', 'badge-success'),
        'occupied': ('Terisi', 'badge-error'),
        'dirty': ('Kotor', 'badge-warning'),
        'maintenance': ('Perbaikan', 'badge-info'),
        'out_of_order': ('Rusak', 'badge-ghost'),
        # Status reservasi
        'confirmed': ('Terkonfirmasi', 'badge-success'),
        'tentative': ('Tentatif', 'badge-warning'),
        'checked_in': ('Check-in', 'badge-info'),
        'checked_out': ('Check-out', 'badge-ghost'),
        'cancelled': ('Dibatalkan', 'badge-error'),
        'no_show': ('Tidak Hadir', 'badge-error'),
        # Tata graha
        'pending': ('Menunggu', 'badge-warning'),
        'in_progress': ('Dikerjakan', 'badge-info'),
        'completed': ('Selesai', 'badge-success'),
        'inspected': ('Diperiksa', 'badge-success'),
        # Pembayaran
        'unpaid': ('Belum Bayar', 'badge-error'),
        'partial': ('Sebagian', 'badge-warning'),
        'paid': ('Lunas', 'badge-success'),
        # Folio
        'open': ('Terbuka', 'badge-info'),
        'closed': ('Ditutup', 'badge-ghost'),
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
