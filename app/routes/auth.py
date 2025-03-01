from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from app.utils.validators import validate_email, validate_password
from app.utils.notifications import send_welcome_email, send_password_reset_email
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        if not all([email, password, first_name, last_name]):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_email(email):
            flash('Invalid email address.', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='patient'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email
            send_welcome_email(user)
            
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again later.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account is not active.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        
        flash('Invalid email or password.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.get_reset_password_token()
            send_password_reset_email(user, token)
            flash('Check your email for password reset instructions.', 'info')
            return redirect(url_for('auth.login'))
            
        flash('Email address not found.', 'error')
        return redirect(url_for('auth.reset_password_request'))
    
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        
        if not validate_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
            
        user.set_password(password)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        
    return render_template('auth/profile.html', user=current_user) 