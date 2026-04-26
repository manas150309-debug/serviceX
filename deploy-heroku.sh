#!/bin/bash
# Deploy to Heroku

# Create Heroku app
heroku create servex-pro

# Add MongoDB Atlas URL (set your own)
heroku config:set MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/servex_pro" -a servex-pro
heroku config:set FLASK_ENV="production" -a servex-pro
heroku config:set SECRET_KEY="your-production-secret-key" -a servex-pro
heroku config:set JWT_SECRET="your-production-jwt-secret" -a servex-pro

# Deploy
git push heroku main

# View logs
heroku logs --tail -a servex-pro
