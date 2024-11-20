from services.settings_service import SettingsService
from flask import request
from flask_login import current_user

def inject_settings():
    """Inject system settings into all templates."""
    try:
        settings = SettingsService.get_all_settings()
        return {
            'site_name': settings.get('site_name', 'Loan System'),
            'site_description': settings.get('site_description', ''),
            'theme_mode': settings.get('theme_mode', 'light'),
            'primary_color': settings.get('primary_color', '#3B82F6'),
            'secondary_color': settings.get('secondary_color', '#1E40AF'),
            'site_logo': settings.get('site_logo', None)
        }
    except Exception as e:
        print(f"Error injecting settings: {str(e)}")
        return {
            'site_name': 'Loan System',
            'site_description': '',
            'theme_mode': 'light',
            'primary_color': '#3B82F6',
            'secondary_color': '#1E40AF',
            'site_logo': None
        }

def inject_navigation():
    """Inject navigation items into all templates."""
    current_path = request.path
    
    # Base navigation items (available to all users)
    nav_items = [
        {
            'url': '/dashboard',
            'icon': 'chart-line',
            'text': 'Dashboard',
            'is_active': current_path == '/dashboard'
        }
    ]
    
    # Admin-only navigation items
    if current_user.is_authenticated and current_user.role == 'Admin':
        admin_items = [
            {
                'url': '/admin/dashboard',
                'icon': 'tachometer-alt',
                'text': 'Admin Dashboard',
                'is_active': current_path == '/admin/dashboard'
            },
            {
                'url': '/admin/users',
                'icon': 'users',
                'text': 'Users',
                'is_active': current_path.startswith('/admin/users')
            },
            {
                'url': '/admin/roles',
                'icon': 'user-tag',
                'text': 'Roles',
                'is_active': current_path.startswith('/admin/roles')
            },
            {
                'url': '/admin/system-settings',
                'icon': 'cog',
                'text': 'Settings',
                'is_active': current_path == '/admin/system-settings'
            }
        ]
        nav_items.extend(admin_items)
    
    return {'navigation_items': nav_items}
