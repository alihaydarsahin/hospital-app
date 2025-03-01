from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment
from app.utils.decorators import doctor_required, patient_required
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Doctor endpoints
@api_bp.route('/doctors', methods=['GET'])
def get_doctors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    department_id = request.args.get('department_id', type=int)
    
    query = Doctor.query
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    doctors = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'doctors': [doctor.to_dict() for doctor in doctors.items],
        'total': doctors.total,
        'pages': doctors.pages,
        'current_page': doctors.page
    })

@api_bp.route('/doctors/<int:id>', methods=['GET'])
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify(doctor.to_dict())

# Department endpoints
@api_bp.route('/departments', methods=['GET'])
def get_departments():
    departments = Department.query.all()
    return jsonify([dept.to_dict() for dept in departments])

@api_bp.route('/departments/<int:id>', methods=['GET'])
def get_department(id):
    department = Department.query.get_or_404(id)
    return jsonify(department.to_dict())

# Appointment endpoints
@api_bp.route('/appointments', methods=['GET'])
@login_required
def get_appointments():
    if current_user.is_patient():
        appointments = Appointment.query.filter_by(patient_id=current_user.id)
    elif current_user.is_doctor():
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        appointments = Appointment.query.filter_by(doctor_id=doctor.id)
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify([apt.to_dict() for apt in appointments])

@api_bp.route('/appointments', methods=['POST'])
@patient_required
def create_appointment():
    data = request.get_json()
    
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    time_str = data.get('time')
    
    if not all([doctor_id, date_str, time_str]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if not doctor.is_available_on(date, time):
        return jsonify({'error': 'Doctor is not available at this time'}), 400
    
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        appointment_date=date,
        appointment_time=time
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 201

@api_bp.route('/appointments/<int:id>', methods=['PUT'])
@login_required
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Check if user has permission
    if not (current_user.is_doctor() and appointment.doctor_id == Doctor.query.filter_by(user_id=current_user.id).first().id) and \
       not (current_user.is_patient() and appointment.patient_id == current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    status = data.get('status')
    
    if status:
        appointment.status = status
        db.session.commit()
    
    return jsonify(appointment.to_dict())

@api_bp.route('/appointments/<int:id>', methods=['DELETE'])
@login_required
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Check if user has permission
    if not (current_user.is_doctor() and appointment.doctor_id == Doctor.query.filter_by(user_id=current_user.id).first().id) and \
       not (current_user.is_patient() and appointment.patient_id == current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointment.status = 'cancelled'
    db.session.commit()
    
    return '', 204 