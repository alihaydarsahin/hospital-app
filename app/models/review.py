from datetime import datetime
from app import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=True)  # Verified if from actual appointment
    is_public = db.Column(db.Boolean, default=True)
    reported_count = db.Column(db.Integer, default=0)
    admin_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, doctor_id, appointment_id, rating, review_text=None, is_anonymous=False):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.appointment_id = appointment_id
        self.rating = min(max(rating, 1), 5)  # Ensure rating is between 1 and 5
        self.review_text = review_text
        self.is_anonymous = is_anonymous

    def report(self):
        """Increment the reported count of the review."""
        self.reported_count += 1
        db.session.commit()

    def add_admin_response(self, response):
        """Add admin response to the review."""
        self.admin_response = response
        db.session.commit()

    def toggle_visibility(self):
        """Toggle the public visibility of the review."""
        self.is_public = not self.is_public
        db.session.commit()

    def to_dict(self):
        """Convert review object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'appointment_id': self.appointment_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'user_name': 'Anonymous' if self.is_anonymous else self.user.full_name,
            'doctor_name': self.doctor.user.full_name,
            'is_anonymous': self.is_anonymous,
            'is_verified': self.is_verified,
            'is_public': self.is_public,
            'reported_count': self.reported_count,
            'admin_response': self.admin_response,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Review {self.id}: {self.rating} stars for Dr. {self.doctor.user.full_name}>' 