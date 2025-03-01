#!/bin/bash

# Exit on error
set -e

echo "Setting up local development environment..."

# Install required packages
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Create self-signed SSL certificate for local development
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Backup existing Nginx config if exists
if [ -f /etc/nginx/sites-available/hospital_app ]; then
    sudo cp /etc/nginx/sites-available/hospital_app /etc/nginx/sites-available/hospital_app.backup
fi

# Create Nginx configuration for local development
cat << EOF | sudo tee /etc/nginx/sites-available/hospital_app
# Development server (localhost)
server {
    listen 80;
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/hospital_app/app/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /uploads {
        internal;
        alias /var/www/hospital_app/uploads;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/hospital_app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Update environment file for local development
cat << EOF > .env.local
FLASK_ENV=development
DEBUG=True
SECRET_KEY=local_development_key
DATABASE_URL=sqlite:///hospital.db
DOMAIN=localhost
ALLOWED_HOSTS=localhost,127.0.0.1
EOF

echo "Local development setup completed!"
echo "Your site is now available at:"
echo "http://localhost"
echo "https://localhost (with self-signed certificate)"
echo ""
echo "For production deployment, you can use free services:"
echo "1. Free domain: Register at Freenom (freenom.com)"
echo "2. Free dynamic DNS: Set up No-IP (noip.com)"
echo "3. Free SSL: Use Let's Encrypt with Certbot" 