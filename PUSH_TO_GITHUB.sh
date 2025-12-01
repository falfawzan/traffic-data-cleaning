#!/bin/bash

# Script to push project to GitHub
# Run this after creating your GitHub repository

echo "=========================================="
echo "GitHub Push Script"
echo "=========================================="
echo ""

# Get repository URL from user
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your repository name: " REPO_NAME

REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo "Repository URL: ${REPO_URL}"
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists"
    read -p "Do you want to update it? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin "${REPO_URL}"
        echo "✅ Remote updated"
    else
        echo "Keeping existing remote"
    fi
else
    git remote add origin "${REPO_URL}"
    echo "✅ Remote added"
fi

# Set branch to main
git branch -M main

echo ""
echo "=========================================="
echo "Ready to push!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure you've created the repository on GitHub.com"
echo "2. You'll need to authenticate when pushing"
echo ""
read -p "Press Enter to push to GitHub (or Ctrl+C to cancel)..."

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "Visit: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Repository doesn't exist on GitHub"
    echo "   - Authentication failed (use Personal Access Token)"
    echo "   - Network issues"
    echo ""
    echo "See GITHUB_PUSH_GUIDE.md for troubleshooting"
fi

