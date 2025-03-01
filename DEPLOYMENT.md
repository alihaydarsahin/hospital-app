# Deployment Checklist

## Pre-deployment Tasks

1. Generate secure passwords:
```bash
# Database password
openssl rand -base64 32

# Admin password
openssl rand -base64 16

# App secret key
openssl rand -hex 32
```

2. Set up email:
- [ ] Create Gmail account for the application
- [ ] Enable 2FA
- [ ] Generate app-specific password

3. Domain setup:
- [ ] Purchase domain
- [ ] Configure DNS A record pointing to your server IP
- [ ] Configure DNS CNAME for www subdomain

## Server Setup

1. Access server:
```bash
ssh root@your-server-ip
```

2. Clone repository:
```bash
git clone https://github.com/alihaydarsahin/hospital-app.git /var/www/hospital_app
cd /var/www/hospital_app
```

3. Run setup script:
```bash
chmod +x scripts/*.sh
./scripts/setup_server.sh
```

4. Configure environment:
```bash
cp .env.production .env
nano .env  # Update with your secure values
```

5. Set up SSL:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

6. Initialize database:
```bash
source venv/bin/activate
flask db upgrade
flask create-admin  # Creates admin user
```

7. Set up backups:
```bash
sudo crontab -e
# Add: 0 2 * * * /var/www/hospital_app/scripts/backup.sh
```

## Post-deployment Tasks

1. Security checks:
- [ ] Verify SSL certificate (https://www.ssllabs.com/ssltest/)
- [ ] Test backup script
- [ ] Verify file permissions
- [ ] Check security headers

2. Application checks:
- [ ] Test user registration
- [ ] Test admin login
- [ ] Test appointment booking
- [ ] Verify email notifications
- [ ] Test file uploads

3. Monitoring setup:
- [ ] Configure Sentry
- [ ] Set up server monitoring
- [ ] Configure log rotation

## Emergency Procedures

1. Database restore:
```bash
gunzip < /var/backups/hospital_app/db_TIMESTAMP.sql.gz | psql hospital_db
```

2. SSL certificate renewal:
```bash
sudo certbot renew
```

3. Application restart:
```bash
sudo systemctl restart hospital_app
sudo supervisorctl restart all
```

## Useful Commands

```bash
# View logs
sudo journalctl -u hospital_app
sudo supervisorctl status

# Check services
sudo systemctl status nginx
sudo systemctl status redis
sudo systemctl status hospital_app

# Database backup
./scripts/backup.sh

# Update application
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart hospital_app
``` 