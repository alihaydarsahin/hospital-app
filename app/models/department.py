from datetime import datetime
from app import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships are defined in the Doctor model

    def __init__(self, name, description=None, image_url=None):
        self.name = name
        self.description = description
        self.image_url = image_url

    @property
    def doctor_count(self):
        """Get total number of doctors in department."""
        return len(self.doctors)

    @property
    def active_doctors(self):
        """Get list of active doctors in department."""
        return [doctor for doctor in self.doctors if doctor.is_available]

    def to_dict(self):
        """Convert department object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'doctor_count': self.doctor_count,
            'active_doctors': len(self.active_doctors),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Department {self.name}>' 