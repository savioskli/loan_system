#!/bin/bash

# Get the commit message
if [ -z "$1" ]; then
    echo "Please provide a commit message"
    exit 1
fi

# Add all changes
git add .

# Commit with the provided message
git commit -m "$1"

# Push to remote
git push

echo "Changes committed and pushed successfully!"
