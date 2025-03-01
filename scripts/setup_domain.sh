#!/bin/bash

# Exit on error
set -e

# Check if domain name is provided
if [ -z "$1" ]; then
    echo "Please provide domain name as argument"
    echo "Usage: $0 yourdomain.com"
    exit 1
fi

DOMAIN=$1

echo "Setting up domain and SSL for $DOMAIN..."

# Install Certbot and Nginx plugin if not already installed
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Backup existing Nginx config if exists
if [ -f /etc/nginx/sites-available/hospital_app ]; then
    sudo cp /etc/nginx/sites-available/hospital_app /etc/nginx/sites-available/hospital_app.backup
fi

# Create Nginx configuration
cat << EOF | sudo tee /etc/nginx/sites-available/hospital_app
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
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

# Get SSL certificate
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# Update environment file with domain
sed -i "s/DOMAIN=.*/DOMAIN=$DOMAIN/" /var/www/hospital_app/.env
sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN/" /var/www/hospital_app/.env

# Set up automatic renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "Domain and SSL setup completed!"
echo "Your site is now available at https://$DOMAIN"
echo "SSL certificate will automatically renew when needed" 