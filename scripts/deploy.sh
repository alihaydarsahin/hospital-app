#!/bin/bash

# Exit on error
set -e

echo "Deploying Hospital Management System..."

# Pull latest changes
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
pip install -r requirements.txt

# Export production environment
export FLASK_ENV=production
export FLASK_APP=run.py

# Run database migrations
flask db upgrade

# Collect static files (if using)
flask static collect

# Restart Gunicorn
sudo systemctl restart hospital_app

# Restart Celery workers
sudo supervisorctl restart celery
sudo supervisorctl restart celery_beat

echo "Deployment completed successfully!" 