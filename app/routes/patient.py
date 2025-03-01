from flask import Blueprint

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patients')
def list_patients():
    return "Patients list" 