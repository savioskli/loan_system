from extensions import db
from datetime import datetime

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    conversation_id = db.Column(db.String(50), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    sql_query = db.Column(db.Text, nullable=True)
    database_used = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}> - {self.conversation_id}'
    
    def to_dict(self):
        """Convert the model to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'message': self.message,
            'response': self.response,
            'sql_query': self.sql_query,
            'database_used': self.database_used,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
