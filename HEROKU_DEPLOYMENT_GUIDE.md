# SERVEX PRO - Heroku Deployment Guide

## Prerequisites
- Heroku account (create at https://www.heroku.com)
- Heroku CLI installed
- MongoDB Atlas account (https://www.mongodb.com/cloud/atlas)
- Git repository pushed to GitHub ✅

## Step 1: Create MongoDB Atlas Database

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create a database user
4. Get your connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/servex_pro
   ```
5. Copy this connection string

## Step 2: Login to Heroku

```bash
heroku login
```
This opens a browser for authentication.

## Step 3: Create Heroku App

```bash
cd /Users/manas/serviceX
heroku create servex-pro
```

Or use Heroku dashboard to create the app if name is taken.

## Step 4: Add Environment Variables

```bash
heroku config:set MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/servex_pro" -a servex-pro
heroku config:set FLASK_ENV="production" -a servex-pro
heroku config:set SECRET_KEY="your-production-secret-key-generate-random" -a servex-pro
heroku config:set JWT_SECRET="your-production-jwt-secret-generate-random" -a servex-pro
heroku config:set GOOGLE_MAPS_API_KEY="your-google-maps-key" -a servex-pro
```

## Step 5: Deploy to Heroku

```bash
git push heroku main
```

## Step 6: Verify Deployment

```bash
# View logs
heroku logs --tail -a servex-pro

# Open app in browser
heroku open -a servex-pro

# Check app status
heroku ps -a servex-pro
```

## Troubleshooting

### App crashes on startup
Check logs:
```bash
heroku logs --tail -a servex-pro
```

### Database connection fails
Verify MONGO_URI is correct and MongoDB cluster allows connections from Heroku IPs.

### Frontend not loading
Frontend files need to be served differently. Consider:
1. Hosting frontend separately on Vercel/Netlify
2. Or serve frontend from Flask static folder

## Frontend Deployment (Vercel - Recommended)

1. Push frontend to GitHub in separate branch or repo
2. Go to https://vercel.com
3. Import GitHub repository
4. Deploy
5. Update API URLs in frontend to point to Heroku backend

## API Endpoint Example

Your backend API will be available at:
```
https://servex-pro.herokuapp.com/api/...
```

Update frontend `js/main.js`:
```javascript
const API_URL = 'https://servex-pro.herokuapp.com/api';
```

## Monitor Performance

```bash
# View dyno type
heroku dynos -a servex-pro

# Scale (upgrade from free dyno)
heroku dyno:scale web=1 -a servex-pro
```

## Useful Heroku Commands

```bash
# View config
heroku config -a servex-pro

# Run one-off process
heroku run python -a servex-pro

# Restart app
heroku restart -a servex-pro

# Scale up
heroku ps:scale web=2 -a servex-pro

# View error logs
heroku logs --tail --source=app -a servex-pro
```
