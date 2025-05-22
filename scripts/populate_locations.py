"""
Script to populate the database with counties, subcounties, and wards.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.append(project_root)

from flask import Flask
from extensions import db
from models.location import County, SubCounty, Ward
from sql.locations_data import KENYA_LOCATIONS

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def populate_locations():
    """
    Populate the database with counties, subcounties, and wards.
    """
    app = create_app()
    with app.app_context():
        # Get existing counties to avoid duplicates
        existing_counties = {c.code: c for c in County.query.all()}
        
        # Track progress
        total_subcounties = sum(len(data['subcounties']) for data in KENYA_LOCATIONS.values())
        total_wards = sum(
            sum(len(wards) for wards in subcounties.values())
            for data in KENYA_LOCATIONS.values()
            for subcounties in [data['subcounties']]
        )
        
        subcounties_added = 0
        wards_added = 0
        
        try:
            for county_code, data in KENYA_LOCATIONS.items():
                # Get or create county
                county = existing_counties.get(county_code)
                if not county:
                    print(f"County {data['name']} not found. Please run the counties migration first.")
                    continue
                
                # Add subcounties and wards
                for subcounty_name, wards in data['subcounties'].items():
                    # Check if subcounty exists
                    subcounty = SubCounty.query.filter_by(
                        name=subcounty_name,
                        county_id=county.id
                    ).first()
                    
                    if not subcounty:
                        subcounty = SubCounty(
                            name=subcounty_name,
                            county_id=county.id,
                            created_by=1,  # System user
                            updated_by=1
                        )
                        db.session.add(subcounty)
                        db.session.flush()  # Get the ID without committing
                        subcounties_added += 1
                        print(f"Added subcounty: {subcounty_name} ({subcounties_added}/{total_subcounties})")
                    
                    # Add wards
                    for ward_name in wards:
                        if not Ward.query.filter_by(
                            name=ward_name,
                            subcounty_id=subcounty.id
                        ).first():
                            ward = Ward(
                                name=ward_name,
                                subcounty_id=subcounty.id,
                                created_by=1,  # System user
                                updated_by=1
                            )
                            db.session.add(ward)
                            wards_added += 1
                            if wards_added % 10 == 0:  # Show progress every 10 wards
                                print(f"Added ward: {ward_name} ({wards_added}/{total_wards})")
                    
                    # Commit after each subcounty to avoid long transactions
                    db.session.commit()
            
            print(f"\nPopulation complete!")
            print(f"Added {subcounties_added} subcounties")
            print(f"Added {wards_added} wards")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            raise

if __name__ == '__main__':
    populate_locations()
