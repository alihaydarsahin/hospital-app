from flask import Blueprint

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments')
def list_appointments():
    return "Appointments list" 