# Quick Deployment Checklist

## Before Deployment

- [ ] GitHub repository created: https://github.com/manas150309-debug/serviceX ✅
- [ ] Code committed and pushed to GitHub ✅
- [ ] Heroku account created: https://www.heroku.com
- [ ] Heroku CLI installed: `brew install heroku`
- [ ] MongoDB Atlas account created: https://www.mongodb.com/cloud/atlas

## Quick Deployment Steps

### 1. Install Heroku CLI (if not already installed)
```bash
brew tap heroku/brew && brew install heroku
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create MongoDB Database
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create database user
4. Copy connection string

### 4. Deploy with One Command
```bash
cd /Users/manas/serviceX
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Create a Heroku app
- Set up all environment variables
- Deploy your code
- Provide you with the live URL

### 5. Check Deployment Status
```bash
heroku logs --tail -a servex-pro
```

## Manual Deployment (if script fails)

```bash
# 1. Create app
heroku create servex-pro

# 2. Add MongoDB connection string
heroku config:set MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/servex_pro" -a servex-pro
heroku config:set FLASK_ENV="production" -a servex-pro
heroku config:set SECRET_KEY="$(openssl rand -hex 32)" -a servex-pro
heroku config:set JWT_SECRET="$(openssl rand -hex 32)" -a servex-pro

# 3. Add Heroku remote
heroku git:remote -a servex-pro

# 4. Deploy
git push heroku main

# 5. Open app
heroku open -a servex-pro
```

## Important Notes

### Free Tier Limitations
- Heroku free dyno sleeps after 30 mins of inactivity
- Free database on MongoDB Atlas has 512MB storage

### For Production
- Upgrade to paid Heroku dyno
- Use paid MongoDB Atlas tier
- Set up custom domain
- Enable HTTPS

### Frontend Deployment
For better performance, deploy frontend separately:
1. Push frontend to GitHub
2. Deploy to Vercel/Netlify
3. Update API URLs to point to Heroku backend

```javascript
// In frontend/js/main.js
const API_URL = 'https://servex-pro.herokuapp.com/api';
```

## Troubleshooting

### App crashes immediately
```bash
heroku logs --tail -a servex-pro
# Check for database connection errors
```

### Database connection fails
- Verify MONGO_URI is correct
- Add Heroku IP to MongoDB Atlas whitelist (allow all IPs temporarily for testing)
- Check credentials

### Cannot push to Heroku
```bash
# Add Heroku remote
git remote remove heroku
heroku git:remote -a servex-pro

# Try push again
git push heroku main
```

## Useful Commands

```bash
# View all config variables
heroku config -a servex-pro

# View logs in real-time
heroku logs --tail -a servex-pro

# Run one-off command
heroku run python -a servex-pro

# Restart app
heroku restart -a servex-pro

# Scale dynos
heroku ps:scale web=2 -a servex-pro

# List all apps
heroku apps

# Rename app
heroku apps:rename newname --app oldname
```

## What's Next?

1. ✅ Backend deployed on Heroku
2. Deploy frontend to Vercel/Netlify
3. Set up custom domain
4. Configure email notifications
5. Add payment processing
6. Monitor performance with Heroku Metrics

## Support

For issues, check:
- Heroku documentation: https://devcenter.heroku.com
- MongoDB documentation: https://docs.mongodb.com
- Flask documentation: https://flask.palletsprojects.com
