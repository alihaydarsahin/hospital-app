import pytest
from flask import url_for
from app.models.user import User

def test_register(client):
    """Test user registration"""
    response = client.post('/auth/register', data={
        'email': 'newuser@example.com',
        'password': 'Password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone': '1234567890'
    })
    assert response.status_code == 302  # Redirect after successful registration
    
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.check_password('Password123')
    assert user.role == 'patient'

def test_login_logout(client, test_user):
    """Test login and logout functionality"""
    # Test login
    response = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    assert b'Welcome' in response.data
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'Login' in response.data

def test_password_reset(client, test_user):
    """Test password reset functionality"""
    # Request password reset
    response = client.post('/auth/reset-password', data={
        'email': test_user.email
    })
    assert response.status_code == 302
    
    # Get token
    token = test_user.get_reset_password_token()
    
    # Reset password
    response = client.post(f'/auth/reset-password/{token}', data={
        'password': 'NewPassword123'
    })
    assert response.status_code == 302
    
    # Verify new password works
    response = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'NewPassword123'
    })
    assert response.status_code == 302

def test_invalid_login(client):
    """Test invalid login attempts"""
    response = client.post('/auth/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert b'Invalid email or password' in response.data

def test_protected_routes(client):
    """Test access to protected routes"""
    # Try accessing protected route without login
    response = client.get('/auth/profile')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_admin_access(client, test_admin):
    """Test admin access restrictions"""
    # Login as admin
    client.post('/auth/login', data={
        'email': test_admin.email,
        'password': 'admin123'
    })
    
    # Access admin route
    response = client.get('/admin/dashboard')
    assert response.status_code == 200

def test_remember_me(client, test_user):
    """Test remember me functionality"""
    response = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'password123',
        'remember': True
    })
    assert response.status_code == 302
    
    # Check for remember_me cookie
    cookies = [cookie.name for cookie in client.cookie_jar]
    assert 'remember_token' in cookies

def test_password_validation(client):
    """Test password validation rules"""
    # Test weak password
    response = client.post('/auth/register', data={
        'email': 'test@example.com',
        'password': 'weak',
        'first_name': 'Test',
        'last_name': 'User'
    })
    assert b'Password must be at least 8 characters' in response.data
    
    # Test password without uppercase
    response = client.post('/auth/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    })
    assert b'Password must contain uppercase' in response.data 