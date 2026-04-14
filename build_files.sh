#!/bin/bash
# Vercel explicitly requires pip to install dependencies before executing build commands
python3.9 -m pip install -r requirements.txt
# Run migrations (Safe to run multiple times, executes if using Supabase based on ENVs)
python3.9 manage.py migrate --noinput
# Collect static files via Whitenoise
python3.9 manage.py collectstatic --noinput --clear

# Automatically create a default Admin login for the dashboard
python3.9 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@mantahotel.com', 'manta2026', display_name='System Admin', role='owner', phone='08123456789')"
