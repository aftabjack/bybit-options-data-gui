#!/bin/bash

# Replace YOUR_USERNAME with your GitHub username
# Replace YOUR_REPO_NAME with your repository name

echo "Setting up GitHub remote..."

# Option 1: Using HTTPS (easier, will ask for username/password or token)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Option 2: Using SSH (requires SSH key setup)
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "Done! Your code is now on GitHub."
echo "Visit: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME"