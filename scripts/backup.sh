#!/bin/bash

# Exit on error
set -e

# Get current date for backup name
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/hospital_app/backups"

echo "Starting backup process..."

# Create backup directory if it doesn't exist
sudo mkdir -p $BACKUP_DIR
sudo chown www-data:www-data $BACKUP_DIR
sudo chmod 750 $BACKUP_DIR

# Backup database
echo "Backing up database..."
cp /var/www/hospital_app/hospital.db "$BACKUP_DIR/hospital_$DATE.db"

# Backup uploads
echo "Backing up uploads..."
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C /var/www/hospital_app uploads/

# Backup environment file
echo "Backing up environment file..."
sudo cp /var/www/hospital_app/.env.production "$BACKUP_DIR/env_$DATE.backup"

# Set correct permissions
sudo chown -R www-data:www-data $BACKUP_DIR
sudo chmod -R 600 $BACKUP_DIR/*

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed! Files saved in $BACKUP_DIR"
echo "Database: hospital_$DATE.db"
echo "Uploads: uploads_$DATE.tar.gz"
echo "Environment: env_$DATE.backup" 