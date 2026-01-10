from db import db
from datetime import datetime

class PendingSubmission(db.Model):
    __tablename__ = 'pending_submissions'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) # new_conference, cancellation, modification
    payload = db.Column(db.JSON, nullable=False) # The data to process
    
    # user_id is now just an integer, not a foreign key, as User model is removed
    user_id = db.Column(db.Integer, nullable=True)
    
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
