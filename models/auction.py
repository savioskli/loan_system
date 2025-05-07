from datetime import datetime
from extensions import db

class Auction(db.Model):
    """Model for auction process tracking"""
    __tablename__ = 'auction'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String(50), nullable=False)
    client_name = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # Residential, Commercial, Industrial, Land
    property_description = db.Column(db.Text, nullable=False)
    valuation_amount = db.Column(db.Float, nullable=False)
    reserve_price = db.Column(db.Float, nullable=False)
    auction_date = db.Column(db.DateTime, nullable=False)
    auction_venue = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Scheduled, Completed, Cancelled, Postponed
    auctioneer_name = db.Column(db.String(100))
    auctioneer_contact = db.Column(db.String(100))
    advertisement_date = db.Column(db.DateTime)
    advertisement_medium = db.Column(db.String(100))
    notes = db.Column(db.Text)
    # Staff assignment fields
    assigned_staff_id = db.Column(db.Integer)
    assigned_staff_name = db.Column(db.String(100))
    supervisor_id = db.Column(db.Integer)
    supervisor_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attachments = db.relationship("AuctionAttachment", back_populates="auction", cascade="all, delete-orphan")
    history = db.relationship("AuctionHistory", back_populates="auction", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Auction {self.id} for Loan {self.loan_id}>'


class AuctionAttachment(db.Model):
    """Model for auction attachments"""
    __tablename__ = 'auction_attachment'

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    auction = db.relationship("Auction", back_populates="attachments")

    def __repr__(self):
        return f'<AuctionAttachment {self.id} for Auction {self.auction_id}>'


class AuctionHistory(db.Model):
    """Model for tracking auction history/updates"""
    __tablename__ = 'auction_history'

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # This will be the new 'action_type'
    action_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True) # Renamed from description, making it nullable as per typical notes fields
    status = db.Column(db.String(50), nullable=False) # e.g., Pending, In Progress, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    auction = db.relationship("Auction", back_populates="history")
    attachments = db.relationship("AuctionHistoryAttachment", back_populates="history", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<AuctionHistory {self.id} for Auction {self.auction_id}>'


class AuctionHistoryAttachment(db.Model):
    """Model for auction history attachments"""
    __tablename__ = 'auction_history_attachments'

    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('auction_history.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    history = db.relationship("AuctionHistory", back_populates="attachments")

    def __repr__(self):
        return f'<AuctionHistoryAttachment {self.id} for History {self.history_id}>'
