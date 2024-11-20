from datetime import datetime
from extensions import db

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20))
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))

    @staticmethod
    def get_setting(key, default=None):
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if setting:
            return setting.setting_value
        return default

    @staticmethod
    def set_setting(key, value, user_id=None):
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
            if user_id:
                setting.updated_by = user_id
        else:
            setting = SystemSettings(
                setting_key=key,
                setting_value=value,
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting
