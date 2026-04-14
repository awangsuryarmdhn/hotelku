"""
Core Mixins — Reusable view mixins for access control and HTMX support.
=======================================================================
Use these in your views to add role checks and HTMX partial rendering.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Restrict a view to users in specific groups (roles).

    Usage:
        class MyView(RoleRequiredMixin, TemplateView):
            allowed_roles = ['Owner', 'Manager', 'Receptionist']
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Superusers always have access
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Check if user belongs to any of the allowed roles
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(role in user_groups for role in self.allowed_roles):
            raise PermissionDenied('You do not have permission to access this page.')

        return super().dispatch(request, *args, **kwargs)


class HtmxViewMixin:
    """
    Automatically use a partial template for HTMX requests.

    If the request is from HTMX, renders only the content partial
    instead of the full page (no sidebar/topbar wrapping).

    Usage:
        class MyView(HtmxViewMixin, TemplateView):
            template_name = 'rooms/list.html'
            # Will auto-use 'rooms/partials/list.html' for HTMX requests
    """

    def get_template_names(self):
        templates = super().get_template_names()

        if getattr(self.request, 'htmx', False):
            # Try to find a partial version of the template
            htmx_templates = []
            for template in templates:
                # Convert 'rooms/list.html' to 'rooms/partials/list.html'
                parts = template.rsplit('/', 1)
                if len(parts) == 2:
                    htmx_templates.append(f'{parts[0]}/partials/{parts[1]}')

            # Use partial if it exists, otherwise fall back to full template
            return htmx_templates + templates

        return templates


class OwnerManagerMixin(RoleRequiredMixin):
    """Shortcut: Only Owner and Manager can access."""
    allowed_roles = ['Owner', 'Manager']


class FrontDeskMixin(RoleRequiredMixin):
    """Shortcut: Owner, Manager, and Receptionist can access."""
    allowed_roles = ['Owner', 'Manager', 'Receptionist']


class HousekeepingMixin(RoleRequiredMixin):
    """Shortcut: Owner, Manager, and Housekeeping staff can access."""
    allowed_roles = ['Owner', 'Manager', 'Housekeeping']


class POSMixin(RoleRequiredMixin):
    """Shortcut: Owner, Manager, and POS Staff can access."""
    allowed_roles = ['Owner', 'Manager', 'POS Staff']
