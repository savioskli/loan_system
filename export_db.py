import os
import subprocess
import datetime

# Create database directory if it doesn't exist
os.makedirs('database', exist_ok=True)

# Generate backup filename with timestamp
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f'database/loan_system_{timestamp}.sql'

# MySQL dump command
dump_command = [
    'mysqldump',
    '-u', 'root',
    'loan_system'
]

# Execute the dump command and write to file
with open(backup_file, 'w') as f:
    subprocess.run(dump_command, stdout=f)

print(f"Database backup created at: {backup_file}")
