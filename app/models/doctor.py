from datetime import datetime
from app import db
from app.models.appointment import Appointment

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    experience_years = db.Column(db.Integer)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    consultation_fee = db.Column(db.Float)
    available_days = db.Column(db.String(100))  # Stored as JSON string: ["Monday", "Tuesday", ...]
    available_time_start = db.Column(db.Time)
    available_time_end = db.Column(db.Time)
    is_available = db.Column(db.Boolean, default=True)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='doctor_profile', uselist=False)
    department = db.relationship('Department', backref='doctors')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    reviews = db.relationship('Review', backref='doctor', lazy='dynamic')

    def __init__(self, user_id, department_id, specialization, qualification, license_number, **kwargs):
        super(Doctor, self).__init__(**kwargs)
        self.user_id = user_id
        self.department_id = department_id
        self.specialization = specialization
        self.qualification = qualification
        self.license_number = license_number

    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

    @property
    def total_reviews(self):
        """Get total number of reviews."""
        return self.reviews.count()

    @property
    def upcoming_appointments(self):
        """Get upcoming appointments."""
        return self.appointments.filter(
            Appointment.appointment_date >= datetime.utcnow()
        ).order_by(Appointment.appointment_date.asc())

    def is_available_on(self, date, time):
        """Check if doctor is available on specific date and time."""
        # Convert date to day name
        day_name = date.strftime("%A")
        
        # Check if doctor works on this day
        if day_name not in self.available_days:
            return False
        
        # Check if time is within working hours
        if time < self.available_time_start or time > self.available_time_end:
            return False
        
        # Check if there's no other appointment at this time
        existing_appointment = self.appointments.filter(
            Appointment.appointment_date == date,
            Appointment.appointment_time == time
        ).first()
        
        return not existing_appointment

    def to_dict(self):
        """Convert doctor object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'specialization': self.specialization,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'license_number': self.license_number,
            'consultation_fee': self.consultation_fee,
            'available_days': self.available_days,
            'available_time_start': str(self.available_time_start) if self.available_time_start else None,
            'available_time_end': str(self.available_time_end) if self.available_time_end else None,
            'is_available': self.is_available,
            'bio': self.bio,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Doctor {self.user.full_name}>' 