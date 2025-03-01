# Hospital Management System

A secure and scalable Flask-based hospital management system with appointment scheduling, notifications, and monitoring.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/yourusername/hospital_app/Deploy%20Hospital%20App)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🏥 Features

- **User Management**
  - Secure authentication with JWT
  - Role-based access control
  - Password reset functionality

- **Appointment System**
  - Schedule and manage appointments
  - Automated email notifications
  - Calendar integration

- **Security Features**
  - SSL/TLS encryption
  - Fail2ban integration
  - UFW firewall configuration
  - Secure file permissions
  - Regular automated backups

- **Monitoring**
  - Prometheus metrics
  - Grafana dashboards
  - System health monitoring
  - Performance tracking

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hospital_app.git
cd hospital_app
```

2. Set up the environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

3. Initialize the database:
```bash
flask db upgrade
```

4. Run the development server:
```bash
flask run
```

## 🔒 Security Features

- **Firewall**: UFW configured to allow only necessary ports
- **Brute Force Protection**: Fail2ban integration
- **File Security**: Strict file permissions
- **SSL/TLS**: Free SSL certificates via Let's Encrypt
- **Secure Headers**: HTTP security headers configured
- **Regular Backups**: Automated daily backups

## 📊 Monitoring

Access system metrics and performance data:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## 🚀 Deployment

1. Generate production secrets:
```bash
python scripts/generate_secrets.py
```

2. Deploy using the script:
```bash
bash scripts/deploy.sh
```

3. Set up monitoring:
```bash
bash scripts/setup_monitoring.sh
bash scripts/setup_dashboards.sh
```

## 💾 Backup

Run manual backup:
```bash
bash scripts/backup.sh
```

Backups are stored in `/var/www/hospital_app/backups` and kept for 7 days.

## 🔧 Configuration

- Environment variables: See `.env.example`
- Nginx configuration: `/etc/nginx/sites-available/hospital_app`
- SystemD services: `/etc/systemd/system/hospital_app.service`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support:
- Create an issue in the GitHub repository
- Check the documentation in the `docs` folder
- Review the deployment guides

## 🙏 Acknowledgments

- Flask and its extensions
- The open source community
- All contributors to this project

## Screenshots

[Add screenshots of your application here] 