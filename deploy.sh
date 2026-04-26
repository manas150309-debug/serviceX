#!/bin/bash

# SERVEX PRO - Complete Deployment Script
# This script sets up and deploys SERVEX PRO to Heroku

set -e  # Exit on error

echo "================================"
echo "SERVEX PRO - Heroku Deployment"
echo "================================"
echo ""

# Check if user is logged into Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged into Heroku. Please run: heroku login"
    exit 1
fi

# Step 1: Create MongoDB Atlas Database
echo "📊 Step 1: MongoDB Setup"
echo "1. Go to https://www.mongodb.com/cloud/atlas"
echo "2. Create a free cluster"
echo "3. Create a database user and copy the connection string"
read -p "Enter your MongoDB connection string (mongodb+srv://...): " MONGO_URI

# Step 2: Create Heroku app
echo ""
echo "🚀 Step 2: Creating Heroku App"
APP_NAME="servex-pro"
heroku apps:create $APP_NAME 2>/dev/null || echo "App $APP_NAME might already exist"

# Step 3: Set environment variables
echo ""
echo "🔐 Step 3: Setting Environment Variables"

# Generate secure keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

heroku config:set \
  MONGO_URI="$MONGO_URI" \
  FLASK_ENV="production" \
  SECRET_KEY="$SECRET_KEY" \
  JWT_SECRET="$JWT_SECRET" \
  -a $APP_NAME

echo "✅ Environment variables set"

# Step 4: Add Heroku git remote
echo ""
echo "📦 Step 4: Adding Heroku Remote"
git remote remove heroku 2>/dev/null || true
heroku git:remote -a $APP_NAME

# Step 5: Deploy
echo ""
echo "🌐 Step 5: Deploying to Heroku"
git push heroku main

# Step 6: Open app
echo ""
echo "✅ Deployment Complete!"
echo ""
echo "Your app is being deployed. Open it with:"
echo "  heroku open -a $APP_NAME"
echo ""
echo "Or visit: https://$APP_NAME.herokuapp.com"
echo ""
echo "View logs with:"
echo "  heroku logs --tail -a $APP_NAME"
