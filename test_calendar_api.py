import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5002'  # Base URL without /api

def test_calendar_api():
    # Create a session to maintain cookies
    session = requests.Session()

    # Login first
    login_data = {
        'username': 'admin',  # replace with your test user credentials
        'password': 'admin'   # replace with your test user credentials
    }
    
    try:
        # Login to get session
        print("\n0. Logging in...")
        response = session.post(f'{BASE_URL}/login', data=login_data)
        if response.status_code != 200:
            print("Login failed!")
            return

        # Test data
        event_data = {
            'title': 'Test Follow-up Call',
            'description': 'Follow up on loan payment',
            'type': 'follow-up',
            'date': datetime.now().date().isoformat(),
            'time': '10:00:00',
            'all_day': False,
            'client_id': None,  # replace with actual client_id if needed
            'loan_id': None     # replace with actual loan_id if needed
        }

        # 1. Create new event
        print("\n1. Testing event creation...")
        response = session.post(f'{BASE_URL}/api/calendar/events', json=event_data)
        print(f"Response: {response.status_code}")
        print(f"Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            event_id = response.json()['id']
            
            # 2. Get all events
            print("\n2. Testing get all events...")
            response = session.get(f'{BASE_URL}/api/calendar/events')
            print(f"Response: {response.status_code}")
            print(f"Data: {json.dumps(response.json(), indent=2)}")
            
            # 3. Update event
            print("\n3. Testing event update...")
            update_data = {
                'title': 'Updated Test Event',
                'description': 'Updated description'
            }
            response = session.put(f'{BASE_URL}/api/calendar/events/{event_id}', json=update_data)
            print(f"Response: {response.status_code}")
            print(f"Data: {json.dumps(response.json(), indent=2)}")
            
            # 4. Delete event
            print("\n4. Testing event deletion...")
            response = session.delete(f'{BASE_URL}/api/calendar/events/{event_id}')
            print(f"Response: {response.status_code}")
            print(f"Data: {json.dumps(response.json(), indent=2)}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Response text: {response.text}")
    finally:
        # Cleanup - logout
        session.get(f'{BASE_URL}/logout')

if __name__ == "__main__":
    test_calendar_api()
