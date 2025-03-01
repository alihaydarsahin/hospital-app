import pytest
from app import create_app, db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment
from datetime import datetime, timedelta
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='patient'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_admin(app):
    admin = User(
        email='admin@hospital.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture
def test_department(app):
    dept = Department(
        name='Cardiology',
        description='Heart and vascular diseases'
    )
    db.session.add(dept)
    db.session.commit()
    return dept

@pytest.fixture
def test_doctor(app, test_department):
    user = User(
        email='doctor@hospital.com',
        first_name='Doctor',
        last_name='Test',
        role='doctor'
    )
    user.set_password('doctor123')
    db.session.add(user)
    db.session.flush()
    
    doctor = Doctor(
        user_id=user.id,
        department_id=test_department.id,
        specialization='Cardiologist',
        qualification='MD, PhD',
        experience_years=10,
        license_number='12345',
        consultation_fee=100.0
    )
    db.session.add(doctor)
    db.session.commit()
    return doctor

@pytest.fixture
def test_appointment(app, test_user, test_doctor):
    appointment = Appointment(
        patient_id=test_user.id,
        doctor_id=test_doctor.id,
        appointment_date=datetime.now().date() + timedelta(days=1),
        appointment_time=datetime.strptime('10:00', '%H:%M').time(),
        status='scheduled'
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment

@pytest.fixture
def auth_headers(test_user, client):
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'} 