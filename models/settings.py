from extensions import db
from datetime import datetime

class SystemSettings(db.Model):
    """System settings model for storing configuration values."""
    __tablename__ = 'system_settings'
    
    # Clear SQLAlchemy's model registry and force table reflection
    __table_args__ = {'extend_existing': True}
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Core fields
    key = db.Column('key', db.String(100), unique=True, nullable=False)
    value = db.Column('value', db.Text)
    
    # Audit fields
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    updated_at = db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column('created_by', db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column('updated_by', db.Integer, db.ForeignKey('staff.id'))

    # Explicitly exclude old columns from mapping
    __mapper_args__ = {
        'include_properties': ['id', 'key', 'value', 'created_at', 'updated_at', 'created_by', 'updated_by']
    }

    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key."""
        try:
            setting = SystemSettings.query.filter_by(key=key).first()
            return setting.value if setting else default
        except Exception as e:
            print(f"Error getting setting {key}: {str(e)}")
            return default

    @staticmethod
    def set_setting(key, value, user_id=None):
        """Set a setting value by key."""
        try:
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                if user_id:
                    setting.updated_by = user_id
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    key=key,
                    value=value,
                    created_by=user_id,
                    updated_by=user_id
                )
                db.session.add(setting)
            
            db.session.commit()
            return setting
        except Exception as e:
            db.session.rollback()
            raise e
