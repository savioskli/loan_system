from extensions import db
from datetime import datetime
from models.system_settings import SystemSettings

__all__ = ['SystemSettings']

# For backward compatibility
class SystemSettings(SystemSettings):
    """System settings model for storing configuration values."""
    __tablename__ = 'system_settings'
    
    # Clear SQLAlchemy's model registry and force table reflection
    __table_args__ = {'extend_existing': True}
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Core fields
    setting_key = db.Column('setting_key', db.String(100), unique=True, nullable=False)
    setting_value = db.Column('setting_value', db.Text)
    setting_type = db.Column('setting_type', db.String(20))
    category = db.Column('category', db.String(50))
    description = db.Column('description', db.String(200))
    
    # Audit fields
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    updated_at = db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column('created_by', db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column('updated_by', db.Integer, db.ForeignKey('staff.id'))

    # Explicitly exclude old columns from mapping
    __mapper_args__ = {
        'include_properties': ['id', 'setting_key', 'setting_value', 'setting_type', 'category', 'description', 'created_at', 'updated_at', 'created_by', 'updated_by']
    }

    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key."""
        try:
            setting = SystemSettings.query.filter_by(setting_key=key).first()
            return setting.setting_value if setting else default
        except Exception as e:
            print(f"Error getting setting {key}: {str(e)}")
            return default

    @staticmethod
    def set_setting(key, value, user_id=None, setting_type='string', category='general', description=None):
        """Set a setting value by key."""
        try:
            setting = SystemSettings.query.filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = value
                if user_id:
                    setting.updated_by = user_id
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=value,
                    setting_type=setting_type,
                    category=category,
                    description=description,
                    created_by=user_id,
                    updated_by=user_id
                )
                db.session.add(setting)
            
            db.session.commit()
            return setting
        except Exception as e:
            db.session.rollback()
            raise e
