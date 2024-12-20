from extensions import db
from datetime import datetime

class CoreBankingTable(db.Model):
    __tablename__ = 'core_banking_tables'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    source = db.Column(db.String(50), nullable=False)  # e.g. 'navision', 'brnet'
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CoreBankingTable {self.name}>'
