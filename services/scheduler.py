from flask_apscheduler import APScheduler
import requests
from datetime import datetime

scheduler = APScheduler()

# Cache for storing the last fetch time and tables
cache = {
    'last_sync': None,
    'tables': []
}

def sync_core_banking_tables():
    """Sync tables from core banking systems every 15 minutes"""
    try:
        # Navision tables
        response = requests.get(
            'http://localhost:5003/api/beta/companies/metadata',
            headers={'Database': 'navision_db'},
            auth=('admin', 'admin123')
        )
        if response.status_code == 200:
            cache['tables'] = response.json().get('value', [])
            cache['last_sync'] = datetime.utcnow()
            print(f"Tables refreshed at {cache['last_sync']}")
    except Exception as e:
        print(f"Error syncing Navision tables: {str(e)}")

def get_cached_tables():
    """Get the cached tables and last sync time"""
    return cache['tables'], cache['last_sync']

def init_scheduler(app):
    """Initialize the scheduler with the Flask app"""
    scheduler.init_app(app)
    
    # Add jobs
    scheduler.add_job(
        id='sync_core_banking_tables',
        func=sync_core_banking_tables,
        trigger='interval',
        minutes=15
    )
    
    # Initial sync
    sync_core_banking_tables()
    
    scheduler.start()
