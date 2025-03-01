from datetime import datetime
from app import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    lab_results = db.Column(db.Text)  # JSON string containing lab results
    vital_signs = db.Column(db.Text)  # JSON string containing vital signs
    allergies = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    documents = db.Column(db.Text)  # JSON string containing document URLs
    is_confidential = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, doctor_id, diagnosis=None, treatment=None, appointment_id=None):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.appointment_id = appointment_id
        self.diagnosis = diagnosis
        self.treatment = treatment

    def add_lab_results(self, results):
        """Add lab results to the medical record."""
        self.lab_results = results
        db.session.commit()

    def add_vital_signs(self, vitals):
        """Add vital signs to the medical record."""
        self.vital_signs = vitals
        db.session.commit()

    def add_document(self, document_url):
        """Add a document URL to the medical record."""
        current_docs = self.documents.split(',') if self.documents else []
        current_docs.append(document_url)
        self.documents = ','.join(current_docs)
        db.session.commit()

    def update_diagnosis(self, diagnosis, treatment=None):
        """Update diagnosis and treatment."""
        self.diagnosis = diagnosis
        if treatment:
            self.treatment = treatment
        db.session.commit()

    def schedule_follow_up(self, follow_up_date):
        """Schedule a follow-up appointment."""
        self.follow_up_date = follow_up_date
        db.session.commit()

    @property
    def needs_follow_up(self):
        """Check if follow-up is needed."""
        if not self.follow_up_date:
            return False
        return self.follow_up_date > datetime.now().date()

    def to_dict(self):
        """Convert medical record object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'appointment_id': self.appointment_id,
            'patient_name': self.user.full_name,
            'doctor_name': self.doctor.user.full_name,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'prescription': self.prescription,
            'notes': self.notes,
            'lab_results': self.lab_results,
            'vital_signs': self.vital_signs,
            'allergies': self.allergies,
            'medical_history': self.medical_history,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'documents': self.documents.split(',') if self.documents else [],
            'is_confidential': self.is_confidential,
            'needs_follow_up': self.needs_follow_up,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<MedicalRecord {self.id}: {self.user.full_name}>' 