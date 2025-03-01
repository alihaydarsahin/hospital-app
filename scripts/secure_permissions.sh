#!/bin/bash

# Exit on error
set -e

echo "Setting secure file permissions..."

# Application directory permissions
sudo chown -R www-data:www-data /var/www/hospital_app
sudo chmod -R 750 /var/www/hospital_app

# Environment file permissions
sudo chown root:www-data /var/www/hospital_app/.env.production
sudo chmod 640 /var/www/hospital_app/.env.production

# SSL certificate permissions
sudo chown root:root /etc/nginx/ssl
sudo chmod 700 /etc/nginx/ssl
sudo chmod 600 /etc/nginx/ssl/*

# Log directory permissions
sudo mkdir -p /var/www/hospital_app/logs
sudo chown www-data:www-data /var/www/hospital_app/logs
sudo chmod 750 /var/www/hospital_app/logs

# Upload directory permissions
sudo mkdir -p /var/www/hospital_app/uploads
sudo chown www-data:www-data /var/www/hospital_app/uploads
sudo chmod 750 /var/www/hospital_app/uploads

# Database file permissions
sudo chown www-data:www-data /var/www/hospital_app/hospital.db
sudo chmod 600 /var/www/hospital_app/hospital.db

echo "File permissions secured!" 