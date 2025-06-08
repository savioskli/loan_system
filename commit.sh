#!/bin/bash

# Get the commit message
if [ -z "$1" ]; then
    echo "Please provide a commit message"
    exit 1
fi

# Create database backup
echo "Creating database backup..."
mysqldump -u root loan_system > database_backup.sql

# Add all changes including the database backup
git add .
git add -f database_backup.sql

# Commit with the provided message
git commit -m "$1"

# Push to remote
git push

echo "Changes and database backup committed and pushed successfully!"
