"""
Core Context Processors — Global template variables.
=====================================================
Makes hotel settings available in every template automatically.
"""
from django.conf import settings


def hotel_context(request):
    """
    Add hotel configuration to every template context.

    Available in templates as:
        {{ hotel_name }}
        {{ hotel_tax_rate }}
        {{ hotel_service_charge }}
    """
    return {
        'hotel_name': settings.HOTEL_NAME,
        'hotel_tax_rate': settings.HOTEL_TAX_RATE,
        'hotel_service_charge': settings.HOTEL_SERVICE_CHARGE,
    }
