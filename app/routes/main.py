from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.appointment import Department, Appointment
from app.models.user import User
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    departments = Department.query.filter_by(is_active=True).all()
    doctor_count = User.query.filter_by(role='doctor', is_active=True).count()
    return render_template('main/index.html',
                         departments=departments,
                         doctor_count=doctor_count)

@main_bp.route('/departments')
def departments():
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('main/departments.html', departments=departments)

@main_bp.route('/department/<int:id>')
def department_detail(id):
    department = Department.query.get_or_404(id)
    doctors = User.query.filter_by(department_id=id, role='doctor', is_active=True).all()
    return render_template('main/department_detail.html',
                         department=department,
                         doctors=doctors)

@main_bp.route('/doctors')
def doctors():
    doctors = User.query.filter_by(role='doctor', is_active=True).all()
    return render_template('main/doctors.html', doctors=doctors)

@main_bp.route('/doctor/<int:id>')
def doctor_detail(id):
    doctor = User.query.filter_by(id=id, role='doctor').first_or_404()
    # Get doctor's available time slots for next 7 days
    available_slots = []
    for i in range(7):
        date = datetime.now().date() + timedelta(days=i)
        slots = get_available_slots(doctor.id, date)
        if slots:
            available_slots.append({
                'date': date.strftime('%Y-%m-%d'),
                'slots': slots
            })
    return render_template('main/doctor_detail.html',
                         doctor=doctor,
                         available_slots=available_slots)

@main_bp.route('/profile')
@login_required
def profile():
    if current_user.is_patient():
        appointments = Appointment.query.filter_by(
            patient_id=current_user.id
        ).order_by(Appointment.date.desc()).all()
        return render_template('main/patient_profile.html',
                             user=current_user,
                             appointments=appointments)
    elif current_user.is_doctor():
        today = datetime.now().date()
        appointments = Appointment.query.filter_by(
            doctor_id=current_user.id,
            date=today
        ).order_by(Appointment.time.asc()).all()
        return render_template('main/doctor_profile.html',
                             user=current_user,
                             appointments=appointments)
    else:
        return render_template('main/profile.html', user=current_user)

@main_bp.route('/api/available-slots/<int:doctor_id>/<string:date>')
def available_slots(doctor_id, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        slots = get_available_slots(doctor_id, date_obj)
        return jsonify({'slots': slots})
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

def get_available_slots(doctor_id, date):
    """Helper function to get available time slots for a doctor on a specific date"""
    from app import app
    
    # Get all appointments for the doctor on the given date
    existing_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=date
    ).all()
    
    # Convert appointment times to set for O(1) lookup
    booked_times = {appointment.time for appointment in existing_appointments}
    
    # Generate all possible time slots
    available_slots = []
    start_hour = app.config['APPOINTMENT_START_HOUR']
    end_hour = app.config['APPOINTMENT_END_HOUR']
    duration = app.config['APPOINTMENT_DURATION']
    
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    
    for hour in range(start_hour, end_hour):
        for minute in range(0, 60, duration):
            slot_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
            
            # Skip slots in the past for today
            if date == current_date and slot_time <= current_time:
                continue
                
            if slot_time not in booked_times:
                available_slots.append(slot_time.strftime("%H:%M"))
    
    return available_slots 