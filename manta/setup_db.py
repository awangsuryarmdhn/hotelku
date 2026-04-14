from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model
import traceback

def setup_database_view(request):
    """
    Emergency Vercel Database Setup Endpoint.
    Runs migrations and creates the admin user remotely.
    """
    response_text = "Starting Database Setup...\n\n"
    
    try:
        # 1. Run migrations
        response_text += "Running migrations...\n"
        call_command('migrate', interactive=False)
        response_text += "Migrations completed successfully!\n\n"
        
        # 2. Create Superuser
        response_text += "Checking Admin User...\n"
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@mantahotel.com', 'manta2026', role='Owner', phone='08123456789')
            response_text += "SUCCESS: Created user 'admin' with password 'manta2026'.\n"
        else:
            response_text += "Admin user already exists.\n"
            
    except Exception as e:
        response_text += f"\nERROR during setup:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        
    return HttpResponse(f"<pre>{response_text}</pre>")
