#!/usr/bin/env python3
import mysql.connector
import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.kenya_locations import KENYA_COUNTIES

def update_subcounty_options():
    # Connect to the database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Add your password here
        database="loan_system"
    )
    cursor = db.cursor()

    # Create options array with all sub-counties
    options = []
    for county, subcounties in KENYA_COUNTIES.items():
        for subcounty in subcounties:
            options.append({
                "label": subcounty,
                "value": subcounty
            })

    # Update the sub-county field options
    options_json = json.dumps(options)
    update_query = """
        UPDATE form_fields 
        SET options = %s 
        WHERE id = 21
    """
    cursor.execute(update_query, (options_json,))
    db.commit()

    print(f"Updated sub-county field with {len(options)} options")
    cursor.close()
    db.close()

if __name__ == "__main__":
    update_subcounty_options()
