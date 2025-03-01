#!/usr/bin/env python3
import secrets
import string
import os

def generate_secure_key(length=32):
    """Generate a secure random string of specified length."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_env_file():
    """Generate production environment file with secure secrets."""
    env_vars = {
        'FLASK_ENV': 'production',
        'DEBUG': 'False',
        'SECRET_KEY': generate_secure_key(64),
        'JWT_SECRET_KEY': generate_secure_key(64),
        'DATABASE_URL': 'sqlite:///hospital.db',
        'REDIS_URL': 'redis://localhost:6379/0',
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': '587',
        'MAIL_USE_TLS': 'True',
        'MAIL_USERNAME': 'your_email@gmail.com',  # Replace this
        'MAIL_PASSWORD': 'your_app_specific_password',  # Replace this
        'DOMAIN': 'localhost',  # Replace with your domain
        'ALLOWED_HOSTS': 'localhost,127.0.0.1',  # Replace with your domain
        'ADMIN_EMAIL': 'admin@yourdomain.com',  # Replace this
        'ADMIN_PASSWORD': generate_secure_key(16),  # Initial admin password
        'PROMETHEUS_MULTIPROC_DIR': '/tmp',
        'METRICS_PORT': '9090'
    }
    
    # Create .env.production file
    with open('.env.production', 'w') as f:
        for key, value in env_vars.items():
            f.write(f'{key}={value}\n')
    
    # Print important information
    print("Production environment file generated: .env.production")
    print("\nIMPORTANT: Please update the following in .env.production:")
    print("1. MAIL_USERNAME and MAIL_PASSWORD with your email credentials")
    print("2. DOMAIN and ALLOWED_HOSTS with your actual domain")
    print("3. ADMIN_EMAIL with your admin email")
    print(f"\nInitial admin password: {env_vars['ADMIN_PASSWORD']}")
    print("Please change this password after first login!")

if __name__ == '__main__':
    if os.path.exists('.env.production'):
        response = input('.env.production already exists. Overwrite? (y/N): ')
        if response.lower() != 'y':
            print('Aborted.')
            exit(0)
    
    generate_env_file()
    print('\nDone! Keep your .env.production file secure and never commit it to version control.') 