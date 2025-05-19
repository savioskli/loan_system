from extensions import db
from flask import current_app
import logging
from sqlalchemy import text

def upgrade_chat_messages():
    """Add rich content support columns to chat_messages table"""
    try:
        # Check if the columns already exist to avoid errors
        with db.engine.connect() as conn:
            # Check if content_type column exists
            result = conn.execute(text(
                "SELECT COUNT(*) AS count FROM information_schema.columns "
                "WHERE table_name='chat_messages' AND column_name='content_type'"
            ))
            content_type_exists = result.fetchone()[0] > 0
            
            # Check if attachments column exists
            result = conn.execute(text(
                "SELECT COUNT(*) AS count FROM information_schema.columns "
                "WHERE table_name='chat_messages' AND column_name='attachments'"
            ))
            attachments_exists = result.fetchone()[0] > 0
            
            # Add content_type column if it doesn't exist
            if not content_type_exists:
                conn.execute(text(
                    "ALTER TABLE chat_messages "
                    "ADD COLUMN content_type VARCHAR(20) DEFAULT 'text' NOT NULL"
                ))
                current_app.logger.info("Added content_type column to chat_messages table")
            
            # Add attachments column if it doesn't exist
            if not attachments_exists:
                conn.execute(text(
                    "ALTER TABLE chat_messages "
                    "ADD COLUMN attachments TEXT NULL"
                ))
                current_app.logger.info("Added attachments column to chat_messages table")
                
            return True
    except Exception as e:
        current_app.logger.error(f"Error upgrading chat_messages table: {str(e)}")
        return False
