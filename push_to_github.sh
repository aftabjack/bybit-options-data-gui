#!/bin/bash

# GitHub repository details
GITHUB_USERNAME="aftabjack"
REPO_NAME="bybit-options-data-gui"

echo "Setting up GitHub remote..."

# Option 1: Using HTTPS (easier, will ask for username/password or token)
git remote add origin https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git

# Option 2: Using SSH (requires SSH key setup)
# git remote add origin git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git

echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "Done! Your code is now on GitHub."
echo "Visit: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"