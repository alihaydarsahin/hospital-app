#!/bin/bash

# Exit on error
set -e

echo "Setting up production server for Hospital Management System..."

# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3.8 \
    python3.8-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    supervisor \
    certbot \
    python3-certbot-nginx \
    git

# Create application directory
sudo mkdir -p /var/www/hospital_app
sudo chown $USER:$USER /var/www/hospital_app

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE hospital_db;
CREATE USER hospital_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE hospital_db TO hospital_user;
\q
EOF

# Set up Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Set up application
cd /var/www/hospital_app
git clone https://github.com/alihaydarsahin/hospital-app.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p logs

# Set up Nginx
sudo cp nginx/hospital_app.conf /etc/nginx/sites-available/hospital_app
sudo ln -s /etc/nginx/sites-available/hospital_app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Set up Supervisor
sudo cp supervisor.conf /etc/supervisor/conf.d/hospital_app.conf
sudo mkdir -p /var/log/supervisor

# Set proper permissions
sudo chown -R www-data:www-data uploads/
sudo chown -R www-data:www-data logs/

# Create systemd service for Gunicorn
sudo tee /etc/systemd/system/hospital_app.service << EOF
[Unit]
Description=Gunicorn instance to serve hospital_app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hospital_app
Environment="PATH=/var/www/hospital_app/venv/bin"
ExecStart=/var/www/hospital_app/venv/bin/gunicorn -c gunicorn_config.py run:app

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Start services
sudo systemctl start hospital_app
sudo systemctl enable hospital_app
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
sudo systemctl restart nginx

echo "Server setup completed! Next steps:"
echo "1. Update the .env file with production values"
echo "2. Set up SSL certificate with: sudo certbot --nginx -d yourdomain.com"
echo "3. Run database migrations: flask db upgrade" 