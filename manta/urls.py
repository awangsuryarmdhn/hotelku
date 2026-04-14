"""
MantaHotel — Root URL Configuration
====================================
All module URLs are included here with clear prefixes.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .setup_db import setup_database_view


urlpatterns = [
    # Remote DB Setup Command
    path('setup-db/', setup_database_view),
    path('docs/', TemplateView.as_view(template_name='docs.html'), name='docs'),

    # PWA Service Worker & Manifest
    path('sw.js', TemplateView.as_view(template_name="sw.js", content_type='application/javascript')),
    path('manifest.json', TemplateView.as_view(template_name="manifest.json", content_type='application/json')),

    # Django admin (auto-generated CRUD for all models)
    path('admin/', admin.site.urls),

    # ── App Routes ──────────────────────────────────
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('rooms/', include('apps.rooms.urls')),
    path('guests/', include('apps.guests.urls')),
    path('reservations/', include('apps.reservations.urls')),
    path('frontdesk/', include('apps.frontdesk.urls')),
    path('housekeeping/', include('apps.housekeeping.urls')),
    path('billing/', include('apps.billing.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('pos/', include('apps.pos.urls')),
    path('reports/', include('apps.reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize Django Admin branding
admin.site.site_header = 'MantaHotel Administration'
admin.site.site_title = 'MantaHotel Admin'
admin.site.index_title = 'Database Management'
