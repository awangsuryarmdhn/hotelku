#!/bin/bash
# Vercel explicitly requires pip to install dependencies before executing build commands
python3.9 -m pip install -r requirements.txt
# Run migrations (Safe to run multiple times, executes if using Supabase based on ENVs)
python3.9 manage.py migrate --noinput
# Collect static files via Whitenoise
python3.9 manage.py collectstatic --noinput --clear
