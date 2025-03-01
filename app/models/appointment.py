from datetime import datetime
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    reason = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)
    prescription = db.Column(db.Text)
    fee_paid = db.Column(db.Boolean, default=False)
    payment_id = db.Column(db.String(100))
    cancelled_by = db.Column(db.String(20))  # user, doctor, admin
    cancellation_reason = db.Column(db.Text)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='patient_appointments')
    doctor = db.relationship('Doctor', foreign_keys=[doctor_id], backref='appointments')
    department = db.relationship('Department', backref='appointments')
    medical_record = db.relationship('MedicalRecord', backref='appointment', uselist=False)
    
    def __init__(self, user_id, doctor_id, appointment_date, appointment_time, reason=None, symptoms=None):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.reason = reason
        self.symptoms = symptoms
    
    def confirm(self):
        """Confirm the appointment."""
        self.status = 'confirmed'
        db.session.commit()
    
    def cancel(self, cancelled_by, reason=None):
        """Cancel the appointment."""
        self.status = 'cancelled'
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        db.session.commit()
    
    def complete(self, notes=None, prescription=None):
        """Mark appointment as completed."""
        self.status = 'completed'
        self.notes = notes
        self.prescription = prescription
        db.session.commit()
    
    def record_payment(self, payment_id):
        """Record payment for appointment."""
        self.fee_paid = True
        self.payment_id = payment_id
        db.session.commit()
    
    def mark_reminder_sent(self):
        """Mark that reminder has been sent."""
        self.reminder_sent = True
        db.session.commit()
    
    @property
    def is_upcoming(self):
        """Check if appointment is upcoming."""
        now = datetime.now()
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime > now
    
    @property
    def can_be_cancelled(self):
        """Check if appointment can be cancelled."""
        return self.status in ['pending', 'confirmed'] and self.is_upcoming
    
    def to_dict(self):
        """Convert appointment object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'patient_name': self.user.full_name,
            'doctor_name': self.doctor.user.full_name,
            'department': self.doctor.department.name,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': str(self.appointment_time),
            'status': self.status,
            'reason': self.reason,
            'symptoms': self.symptoms,
            'notes': self.notes,
            'prescription': self.prescription,
            'fee_paid': self.fee_paid,
            'payment_id': self.payment_id,
            'cancelled_by': self.cancelled_by,
            'cancellation_reason': self.cancellation_reason,
            'is_upcoming': self.is_upcoming,
            'can_be_cancelled': self.can_be_cancelled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.user.full_name} with Dr. {self.doctor.user.full_name}>'

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    doctors = db.relationship('User', backref='department', lazy='dynamic')
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'doctor_count': self.doctors.count()
        }
    
    def __repr__(self):
        return f'<Department {self.name}>'

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, appointment_id, patient_id, diagnosis=None, treatment=None, prescription=None, notes=None):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.diagnosis = diagnosis
        self.treatment = treatment
        self.prescription = prescription
        self.notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'prescription': self.prescription,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} for Appointment {self.appointment_id}>' 