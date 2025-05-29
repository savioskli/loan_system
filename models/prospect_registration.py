from extensions import db
from datetime import datetime

class ProspectRegistration(db.Model):
    """Model for prospect registration data"""
    __tablename__ = 'prospect_registration_data'
    
    # Core fields that exist in the database
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    is_active = db.Column(db.Boolean, default=True)
    first_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.JSON)
    identification_type = db.Column(db.String(100))
    identification_number = db.Column(db.String(255))
    serial_number = db.Column(db.String(255))
    birth_date = db.Column(db.Date)
    mobile_number = db.Column(db.String(255))
    email_address = db.Column(db.String(255))
    postal_address = db.Column(db.String(255))
    postal_code = db.Column(db.String(255))
    postal_town = db.Column(db.String(100))
    county = db.Column(db.String(100))
    status = db.Column(db.String(255))
    
    # Client type relationship
    client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=True)
    client_type = db.relationship('ClientType', backref='prospects')
    
    # Product relationship
    # product = db.relationship('Product', backref='prospects')
    
    # Note: The following columns are commented out as they don't exist in the database
    # If you need these fields, you'll need to create a database migration to add them
    # marital_status = db.Column(db.String(20), nullable=True)
    # nationality = db.Column(db.String(50), nullable=True)
    # sub_county = db.Column(db.String(100), nullable=True)
    # ward = db.Column(db.String(100), nullable=True)
    # estate = db.Column(db.String(100), nullable=True)
    # house_number = db.Column(db.String(50), nullable=True)
    # occupation = db.Column(db.String(100), nullable=True)
    # employer_name = db.Column(db.String(100), nullable=True)
    # employment_type = db.Column(db.String(50), nullable=True)
    # monthly_income = db.Column(db.Numeric(15, 2), nullable=True)
    # other_income = db.Column(db.Numeric(15, 2), nullable=True)
    # income_source = db.Column(db.String(100), nullable=True)
    # next_of_kin_name = db.Column(db.String(100), nullable=True)
    # next_of_kin_phone = db.Column(db.String(20), nullable=True)
    # next_of_kin_relationship = db.Column(db.String(50), nullable=True)
    # next_of_kin_id = db.Column(db.String(50), nullable=True)
    # purpose_of_visit = db.Column(db.String(100), nullable=True)
    # purpose_description = db.Column(db.Text, nullable=True)
    # product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    # is_converted = db.Column(db.Boolean, default=False, nullable=True)
    # client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary with only fields that exist in the database"""
        result = {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'id_type': self.identification_type,
            'id_number': self.identification_number,
            'email': self.email_address,
            'phone': self.mobile_number,
            'date_of_birth': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'county': self.county,
            'postal_code': self.postal_code,
            'postal_town': self.postal_town,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'updated_by': self.updated_by,
            'serial_number': self.serial_number,
            'postal_address': self.postal_address
        }
        
        # Add optional fields if they exist
        if hasattr(self, 'marital_status'):
            result['marital_status'] = self.marital_status
        if hasattr(self, 'nationality'):
            result['nationality'] = self.nationality
        if hasattr(self, 'sub_county'):
            result['sub_county'] = self.sub_county
        if hasattr(self, 'ward'):
            result['ward'] = self.ward
        if hasattr(self, 'estate'):
            result['estate'] = self.estate
        if hasattr(self, 'house_number'):
            result['house_number'] = self.house_number
        if hasattr(self, 'occupation'):
            result['occupation'] = self.occupation
        if hasattr(self, 'employer_name'):
            result['employer_name'] = self.employer_name
        if hasattr(self, 'employment_type'):
            result['employment_type'] = self.employment_type
        if hasattr(self, 'monthly_income'):
            result['monthly_income'] = float(self.monthly_income) if self.monthly_income is not None else None
        if hasattr(self, 'other_income'):
            result['other_income'] = float(self.other_income) if self.other_income is not None else None
        if hasattr(self, 'income_source'):
            result['income_source'] = self.income_source
        if hasattr(self, 'next_of_kin_name'):
            result['next_of_kin_name'] = self.next_of_kin_name
        if hasattr(self, 'next_of_kin_phone'):
            result['next_of_kin_phone'] = self.next_of_kin_phone
        if hasattr(self, 'next_of_kin_relationship'):
            result['next_of_kin_relationship'] = self.next_of_kin_relationship
        if hasattr(self, 'next_of_kin_id'):
            result['next_of_kin_id'] = self.next_of_kin_id
        if hasattr(self, 'purpose_of_visit'):
            result['purpose_of_visit'] = self.purpose_of_visit
        if hasattr(self, 'purpose_description'):
            result['purpose_description'] = self.purpose_description
        if hasattr(self, 'product_id'):
            result['product_id'] = self.product_id
        if hasattr(self, 'is_converted'):
            result['is_converted'] = self.is_converted
        if hasattr(self, 'client_type_id'):
            result['client_type_id'] = self.client_type_id
            
        return result
    
    def __repr__(self):
        return f'<ProspectRegistration {self.first_name} {self.last_name}>'
