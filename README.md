# Hospital Management System

A Flask-based hospital management system with appointment scheduling, notifications, and monitoring.

## Features

- User authentication and authorization
- Appointment scheduling and management
- Email notifications for appointments
- Daily reports generation
- System monitoring with Prometheus and Grafana
- Secure SSL/TLS encryption

## Requirements

- Python 3.9+
- Redis (for task queue)
- Nginx (for reverse proxy)
- SQLite (database)

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hospital_app.git
cd hospital_app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the environment:
```bash
cp .env.local .env
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## Deployment (Free Options)

1. Clone the repository on your server:
```bash
git clone https://github.com/yourusername/hospital_app.git
cd hospital_app
```

2. Run the deployment script:
```bash
bash scripts/deploy.sh
```

This will:
- Set up Python environment
- Install dependencies
- Configure Nginx
- Set up SSL certificate
- Start the application

3. Set up monitoring (optional):
```bash
bash scripts/setup_monitoring.sh
bash scripts/setup_dashboards.sh
```

## Free Services Used

- **Domain**: Can use Freenom for free domain
- **SSL**: Let's Encrypt (free certificates)
- **Hosting**: Can be deployed on free tier of cloud providers
- **Database**: SQLite (included)
- **Monitoring**: Prometheus + Grafana (open source)

## GitHub Actions

The repository includes GitHub Actions for:
- Running tests
- Code coverage reporting
- Automated deployment

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email support@yourdomain.com or create an issue in the GitHub repository.

## Acknowledgments

- Flask and its extensions
- All contributors who participate in this project
- The open source community

## Screenshots

[Add screenshots of your application here] 