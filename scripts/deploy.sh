#!/bin/bash

# Exit on error
set -e

echo "Deploying Hospital App..."

# Create application directory
sudo mkdir -p /var/www/hospital_app
cd /var/www/hospital_app

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx redis-server ufw fail2ban

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable

# Configure fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Generate production secrets if not exists
if [ ! -f .env.production ]; then
    python scripts/generate_secrets.py
fi

# Setup database
flask db upgrade

# Setup static files
flask static-build

# Setup systemd service for the application
cat << EOF | sudo tee /etc/systemd/system/hospital_app.service
[Unit]
Description=Hospital App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/hospital_app
Environment="PATH=/var/www/hospital_app/venv/bin"
ExecStart=/var/www/hospital_app/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"
Restart=always
# Security measures
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

# Setup systemd service for Celery worker
cat << EOF | sudo tee /etc/systemd/system/hospital_app_worker.service
[Unit]
Description=Hospital App Celery Worker
After=network.target redis-server.service

[Service]
User=www-data
WorkingDirectory=/var/www/hospital_app
Environment="PATH=/var/www/hospital_app/venv/bin"
ExecStart=/var/www/hospital_app/venv/bin/celery -A app.celery worker --loglevel=info
Restart=always
# Security measures
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

# Set secure permissions
bash scripts/secure_permissions.sh

# Start and enable services
sudo systemctl daemon-reload
sudo systemctl enable hospital_app
sudo systemctl enable hospital_app_worker
sudo systemctl start hospital_app
sudo systemctl start hospital_app_worker

# Run the domain setup script
bash scripts/setup_domain_free.sh

echo "Deployment completed!"
echo "Your application is now running at http://localhost"
echo ""
echo "Security measures implemented:"
echo "1. UFW firewall configured"
echo "2. Fail2ban installed and configured"
echo "3. Secure file permissions set"
echo "4. SystemD service hardening applied"
echo ""
echo "Next steps:"
echo "1. Set up monitoring using scripts/setup_monitoring.sh"
echo "2. Set up dashboards using scripts/setup_dashboards.sh"
echo "3. Configure your free domain from Freenom if needed"
echo "4. Change the admin password immediately after first login" 