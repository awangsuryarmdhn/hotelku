"""
MantaHotel — Vercel WSGI Entrypoint
====================================
This file exposes the Django WSGI app for Vercel's Python runtime.
Vercel looks for an 'app' variable in api/index.py.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path so Django can find everything
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manta.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
