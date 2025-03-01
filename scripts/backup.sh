#!/bin/bash

# Exit on error
set -e

# Configuration
BACKUP_DIR="/var/backups/hospital_app"
DB_NAME="hospital_db"
DB_USER="hospital_user"
UPLOADS_DIR="/var/www/hospital_app/uploads"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
echo "Backing up database..."
PGPASSWORD="your-secure-password" pg_dump -U "$DB_USER" -h localhost "$DB_NAME" > "$BACKUP_DIR/db_$TIMESTAMP.sql"

# Backup uploads directory
echo "Backing up uploads..."
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" -C "$(dirname "$UPLOADS_DIR")" "$(basename "$UPLOADS_DIR")"

# Compress database backup
gzip "$BACKUP_DIR/db_$TIMESTAMP.sql"

# Delete old backups
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully!"
echo "Database: $BACKUP_DIR/db_$TIMESTAMP.sql.gz"
echo "Uploads: $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" 