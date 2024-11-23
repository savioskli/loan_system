from extensions import db
from models.system_settings import SystemSettings
from app import create_app
from sqlalchemy import text

def fix_settings_table():
    try:
        app = create_app()
        with app.app_context():
            with db.engine.connect() as connection:
                # First, copy data from old columns to new columns if they exist
                try:
                    connection.execute(text(
                        "UPDATE system_settings "
                        "SET setting_key = `key`, setting_value = value "
                        "WHERE setting_key IS NULL AND `key` IS NOT NULL"
                    ))
                    print("Successfully copied data from old columns")
                except:
                    pass

                # Drop the old columns
                try:
                    connection.execute(text("ALTER TABLE system_settings DROP COLUMN `key`"))
                    connection.execute(text("ALTER TABLE system_settings DROP COLUMN `value`"))
                    print("Successfully dropped old columns")
                except:
                    pass

                # Make sure the new columns exist
                result = connection.execute(text(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = 'loan_system' "
                    "AND TABLE_NAME = 'system_settings' "
                    "AND COLUMN_NAME = 'setting_key'"
                ))
                if result.scalar() == 0:
                    connection.execute(text(
                        "ALTER TABLE system_settings "
                        "ADD COLUMN setting_key VARCHAR(100) NOT NULL, "
                        "ADD COLUMN setting_value TEXT, "
                        "ADD COLUMN setting_type VARCHAR(20), "
                        "ADD COLUMN category VARCHAR(50), "
                        "ADD COLUMN description VARCHAR(200)"
                    ))
                    print("Successfully added setting columns")
                
                # Add unique constraint on setting_key if it doesn't exist
                try:
                    connection.execute(text(
                        "ALTER TABLE system_settings "
                        "ADD UNIQUE INDEX idx_setting_key (setting_key)"
                    ))
                    print("Successfully added unique constraint on setting_key")
                except:
                    print("Unique constraint might already exist")

                connection.commit()
                
                # Insert default settings if they don't exist
                result = connection.execute(text(
                    "SELECT COUNT(*) FROM system_settings WHERE setting_key = 'site_name'"
                ))
                if result.scalar() == 0:
                    settings = SystemSettings(
                        setting_key='site_name',
                        setting_value='Loan Origination & Appraisal System',
                        setting_type='string',
                        category='general',
                        description='Site name displayed in the header',
                        updated_by=1
                    )
                    db.session.add(settings)
                    db.session.commit()
                    print("Successfully added default settings")
                else:
                    print("Default settings already exist")
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    fix_settings_table()
