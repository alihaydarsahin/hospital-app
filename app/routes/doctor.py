from flask import Blueprint

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctors')
def list_doctors():
    return "Doctors list" 