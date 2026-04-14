"""
MantaHotel — WSGI Configuration
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manta.settings')
application = get_wsgi_application()

# Vercel requires 'app' variable
app = application
