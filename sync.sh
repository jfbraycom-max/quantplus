#!/bin/bash

# Use the first argument as the commit message, or default to a standard message
MESSAGE=${1:-"Update application code"}

echo "Adding changes..."
git add .

echo "Committing with message: '$MESSAGE'"
git commit -m "$MESSAGE"

echo "Pushing to GitHub..."
git push origin main

echo "Done!"
