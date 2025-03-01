import pytest
from datetime import datetime, timedelta
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.department import Department

def test_list_doctors(client, test_doctor):
    """Test listing doctors"""
    response = client.get('/api/doctors')
    assert response.status_code == 200
    assert test_doctor.name in response.get_json()['doctors'][0]['name']

def test_doctor_search(client, test_doctor):
    """Test doctor search functionality"""
    # Search by name
    response = client.get(f'/api/doctors?search={test_doctor.name}')
    assert response.status_code == 200
    assert test_doctor.name in response.get_json()['doctors'][0]['name']
    
    # Search by department
    response = client.get(f'/api/doctors?department={test_doctor.department.name}')
    assert response.status_code == 200
    assert test_doctor.name in response.get_json()['doctors'][0]['name']

def test_doctor_availability(client, test_doctor, test_user, auth_headers):
    """Test doctor availability slots"""
    # Get available slots
    tomorrow = datetime.now() + timedelta(days=1)
    response = client.get(
        f'/api/doctors/{test_doctor.id}/availability?date={tomorrow.strftime("%Y-%m-%d")}',
        headers=auth_headers
    )
    assert response.status_code == 200
    slots = response.get_json()['slots']
    assert len(slots) > 0

def test_book_appointment(client, test_doctor, test_user, auth_headers):
    """Test appointment booking"""
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_data = {
        'doctor_id': test_doctor.id,
        'date': tomorrow.strftime('%Y-%m-%d'),
        'time': '10:00',
        'reason': 'Regular checkup'
    }
    
    response = client.post(
        '/api/appointments',
        json=appointment_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    
    # Verify appointment was created
    appointment = Appointment.query.filter_by(
        doctor_id=test_doctor.id,
        patient_id=test_user.id
    ).first()
    assert appointment is not None
    assert appointment.status == 'pending'

def test_cancel_appointment(client, test_appointment, auth_headers):
    """Test appointment cancellation"""
    response = client.post(
        f'/api/appointments/{test_appointment.id}/cancel',
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify appointment was cancelled
    appointment = Appointment.query.get(test_appointment.id)
    assert appointment.status == 'cancelled'

def test_doctor_rating(client, test_doctor, test_appointment, auth_headers):
    """Test doctor rating functionality"""
    # Complete the appointment first
    test_appointment.status = 'completed'
    
    # Submit rating
    rating_data = {
        'rating': 5,
        'review': 'Excellent service'
    }
    response = client.post(
        f'/api/doctors/{test_doctor.id}/rate',
        json=rating_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify rating was recorded
    doctor = Doctor.query.get(test_doctor.id)
    assert doctor.average_rating > 0

def test_department_list(client):
    """Test department listing"""
    response = client.get('/api/departments')
    assert response.status_code == 200
    departments = response.get_json()['departments']
    assert len(departments) > 0

def test_doctor_schedule(client, test_doctor, auth_headers):
    """Test doctor schedule management"""
    schedule_data = {
        'monday': ['09:00-12:00', '14:00-17:00'],
        'tuesday': ['09:00-12:00', '14:00-17:00'],
        'wednesday': ['09:00-12:00'],
        'thursday': ['14:00-17:00'],
        'friday': ['09:00-12:00', '14:00-17:00']
    }
    
    response = client.put(
        f'/api/doctors/{test_doctor.id}/schedule',
        json=schedule_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify schedule was updated
    doctor = Doctor.query.get(test_doctor.id)
    assert doctor.schedule == schedule_data 