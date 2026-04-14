"""
Core Middleware — Custom middleware for MantaHotel.
===================================================
TimezoneMiddleware: Sets the timezone based on hotel config.
"""
from django.utils import timezone as tz
from django.conf import settings
import zoneinfo


class TimezoneMiddleware:
    """
    Set the timezone for each request based on the hotel's timezone setting.
    Default: Asia/Makassar (WITA — Bali timezone).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            hotel_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
            tz.activate(hotel_tz)
        except Exception:
            tz.deactivate()

        response = self.get_response(request)
        return response
