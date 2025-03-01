import secrets
import os

def generate_secrets():
    secrets_dict = {
        'DB_PASSWORD': secrets.token_urlsafe(32),
        'ADMIN_PASSWORD': secrets.token_urlsafe(16),
        'SECRET_KEY': secrets.token_hex(32),
        'JWT_SECRET_KEY': secrets.token_hex(32),
    }
    
    with open('production_secrets.txt', 'w') as f:
        for key, value in secrets_dict.items():
            f.write(f'{key}={value}\n')

if __name__ == '__main__':
    generate_secrets() 