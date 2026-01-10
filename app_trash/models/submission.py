from app.extensions import db
from datetime import datetime

class PendingSubmission(db.Model):
    __tablename__ = 'pending_submissions'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) # new_conference, cancellation, modification
    payload = db.Column(db.JSON, nullable=False) # The data to process
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('submissions', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else 'unknown',
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'payload': self.payload
        }
