from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Admin yetkisi gerektiren route'lar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """Decorator for routes that require doctor authorization"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_doctor():
            flash('Access denied. Doctor authorization required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    """Decorator for routes that require patient authorization"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_patient():
            flash('Access denied. Patient authorization required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """Aktif kullanıcı gerektiren route'lar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_active:
            flash('Hesabınız aktif değil.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def prevent_authenticated(f):
    """Giriş yapmış kullanıcıların erişemeyeceği route'lar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def check_appointment_owner(f):
    """Randevu sahibi kontrolü yapan dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.appointment import Appointment
        
        appointment_id = kwargs.get('id')
        if not appointment_id:
            flash('Geçersiz randevu.', 'error')
            return redirect(url_for('main.index'))
        
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if current_user.is_patient() and appointment.patient_id != current_user.id:
            flash('Bu randevuya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.index'))
            
        if current_user.is_doctor() and appointment.doctor_id != current_user.id:
            flash('Bu randevuya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(f):
    """Decorator for rate limiting based on user or IP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        from app import redis_client
        from datetime import datetime, timedelta
        
        # Kullanıcı veya IP bazlı rate limiting
        key = f"rate_limit:{request.remote_addr}"
        if current_user.is_authenticated:
            key = f"rate_limit:user_{current_user.id}"
        
        # Rate limit kontrolü
        current = redis_client.get(key)
        if current is not None and int(current) > 100:  # Örnek: 100 istek/dakika
            flash('Çok fazla istek gönderdiniz. Lütfen biraz bekleyin.', 'error')
            return redirect(url_for('main.index'))
        
        # Rate limit sayacını güncelle
        pipe = redis_client.pipeline()
        if current is None:
            pipe.setex(key, timedelta(minutes=1), 1)
        else:
            pipe.incr(key)
        pipe.execute()
        
        return f(*args, **kwargs)
    return decorated_function 