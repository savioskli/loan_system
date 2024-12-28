import random
import datetime
import json

# Sample data for generating random correspondence
clients = [
    {'id': 1, 'name': 'Client A'},
    {'id': 2, 'name': 'Client B'},
    {'id': 3, 'name': 'Client C'},
]

correspondence_types = ['SMS', 'Email', 'Call', 'Letter', 'Visit']

# Function to generate random correspondence data
def generate_random_correspondence():
    correspondence = {
        'account_no': random.randint(1000, 9999),
        'client_name': random.choice(clients)['name'],
        'type': random.choice(correspondence_types),
        'message': 'This is a random message for testing.',
        'status': 'pending',
        'sent_by': 'User1',
        'recipient': 'Recipient1',
        'delivery_status': 'not sent',
        'delivery_time': datetime.datetime.now().isoformat(),
        'call_duration': random.randint(0, 300),
        'call_outcome': 'Completed',
        'location': 'Location A',
        'visit_purpose': 'Follow-up',
        'visit_outcome': 'Successful',
        'staff_id': random.randint(1, 10),
        'loan_id': random.randint(1, 50),
        'attachment_path': '/path/to/attachment'
    }
    return correspondence

# Generate a list of random correspondence
random_correspondences = [generate_random_correspondence() for _ in range(10)]

# Save to a JSON file
with open('random_correspondence.json', 'w') as f:
    json.dump(random_correspondences, f, indent=4)

print('Random correspondence data generated and saved to random_correspondence.json')
