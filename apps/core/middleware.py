"""
Core Middleware — Custom middleware for Grand Nirwana Hotel PMS.
================================================================
TimezoneMiddleware: Sets the timezone based on hotel config.
"""
from django.utils import timezone as tz
from django.conf import settings
import zoneinfo


class TimezoneMiddleware:
    """
    Set the timezone for each request based on the hotel's timezone setting.
    Configured in .env as TIMEZONE= (default: Asia/Pontianak for Grand Nirwana).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            hotel_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
            tz.activate(hotel_tz)
        except zoneinfo.ZoneInfoNotFoundError:
            # If the timezone name from .env is invalid, fall back to UTC safely.
            # Fix: check your TIMEZONE= value in the .env file.
            tz.deactivate()

        response = self.get_response(request)
        return response
