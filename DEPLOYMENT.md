# 🚀 Deployment Guide - AI Puzzle Game

Complete guide for deploying your application to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Database Setup (Optional)](#database-setup-optional)
7. [SSL/HTTPS Configuration](#ssl-https-configuration)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## 📦 Prerequisites

Before deploying, ensure you have:

- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ Git installed
- ✅ Unsplash API key (get from https://unsplash.com/developers)
- ✅ Domain name (optional, for production)
- ✅ Cloud account (Heroku, AWS, DigitalOcean, etc.)

---

## 💻 Local Deployment

### Step 1: Clone Repository
```bash
git clone <your-repository-url>
cd ai-puzzle-game
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your configuration
```

**Edit `backend/.env`:**
```bash
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
FLASK_ENV=production

UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
UNSPLASH_SECRET_KEY=your_unsplash_secret_key_here

CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

**Run Backend:**
```bash
# Development
python app.py

# Production (with Gunicorn)
gunicorn -c run.py app:app
```

### Step 3: Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

**Edit `frontend/.env`:**
```bash
REACT_APP_API_URL=https://your-backend-url.com/api
NODE_ENV=production
```

**Build Frontend:**
```bash
npm run build
```

---

## ☁️ Cloud Deployment Options

### Option 1: Heroku (Easiest)
### Option 2: AWS EC2 (Most Flexible)
### Option 3: DigitalOcean (Good Balance)
### Option 4: Vercel (Frontend) + Railway (Backend)

---

## 🎯 Backend Deployment

### Option A: Heroku Deployment

#### 1. Install Heroku CLI
```bash
# Install Heroku CLI
# Mac:
brew tap heroku/brew && brew install heroku

# Windows:
# Download from https://devcenter.heroku.com/articles/heroku-cli

# Linux:
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Create Heroku App
```bash
cd backend

# Login to Heroku
heroku login

# Create app
heroku create your-puzzle-backend

# Add Python buildpack
heroku buildpacks:set heroku/python
```

#### 3. Configure Heroku
```bash
# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set UNSPLASH_ACCESS_KEY=your-key
heroku config:set UNSPLASH_SECRET_KEY=your-secret
heroku config:set FLASK_ENV=production
heroku config:set DEBUG=False
```

#### 4. Create `Procfile` in backend directory
```bash
web: gunicorn app:app
```

#### 5. Create `runtime.txt` in backend directory
```
python-3.11.0
```

#### 6. Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### 7. Open App
```bash
heroku open
```

---

### Option B: AWS EC2 Deployment

#### 1. Launch EC2 Instance

1. Go to AWS Console → EC2
2. Launch Instance
3. Select Ubuntu 22.04 LTS
4. Choose t2.medium (or larger for better performance)
5. Configure Security Group:
   - Allow HTTP (80)
   - Allow HTTPS (443)
   - Allow SSH (22)
6. Create/select key pair
7. Launch instance

#### 2. Connect to Instance
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install system dependencies for OpenCV
sudo apt install libgl1-mesa-glx libglib2.0-0 -y
```

#### 4. Clone and Setup Application
```bash
# Clone repository
git clone <your-repo-url>
cd ai-puzzle-game/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 5. Configure Environment
```bash
# Create .env file
nano .env
```

Add your configuration:
```bash
SECRET_KEY=your-secret-key
UNSPLASH_ACCESS_KEY=your-key
UNSPLASH_SECRET_KEY=your-secret
FLASK_ENV=production
DEBUG=False
```

#### 6. Create Systemd Service
```bash
sudo nano /etc/systemd/system/puzzle-backend.service
```

Add:
```ini
[Unit]
Description=AI Puzzle Game Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-puzzle-game/backend
Environment="PATH=/home/ubuntu/ai-puzzle-game/backend/venv/bin"
ExecStart=/home/ubuntu/ai-puzzle-game/backend/venv/bin/gunicorn -c run.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 7. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start puzzle-backend
sudo systemctl enable puzzle-backend
sudo systemctl status puzzle-backend
```

#### 8. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/puzzle-backend
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/puzzle-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Option C: Railway Deployment (Modern & Easy)

#### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

#### 2. Login and Deploy
```bash
cd backend
railway login
railway init
railway up
```

#### 3. Configure Environment Variables

In Railway dashboard:
- Add all environment variables from `.env`
- Set `PORT=5000`

#### 4. Deploy
```bash
railway up
```

Railway will automatically:
- Detect Python
- Install dependencies
- Start with Gunicorn

---

## 🎨 Frontend Deployment

### Option A: Vercel (Recommended for React)

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Deploy
```bash
cd frontend
vercel login
vercel --prod
```

#### 3. Configure Environment Variables

In Vercel dashboard, add:
```
REACT_APP_API_URL=https://your-backend-url.com/api
```

#### 4. Custom Domain (Optional)

In Vercel dashboard:
- Go to Settings → Domains
- Add your custom domain
- Follow DNS configuration instructions

---

### Option B: Netlify

#### 1. Install Netlify CLI
```bash
npm install -g netlify-cli
```

#### 2. Build and Deploy
```bash
cd frontend
npm run build
netlify login
netlify deploy --prod
```

#### 3. Configure

- Set build command: `npm run build`
- Set publish directory: `build`
- Add environment variables in Netlify dashboard

---

### Option C: AWS S3 + CloudFront

#### 1. Build Application
```bash
cd frontend
npm run build
```

#### 2. Create S3 Bucket
```bash
aws s3 mb s3://your-puzzle-game
aws s3 sync build/ s3://your-puzzle-game
```

#### 3. Configure S3 for Static Website

- Enable static website hosting
- Set index.html as index document
- Make bucket public

#### 4. Create CloudFront Distribution

- Origin: Your S3 bucket
- Enable HTTPS
- Set default root object: index.html

---

## 🗄️ Database Setup (Optional - For User Authentication)

### PostgreSQL on Heroku
```bash
# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Get database URL
heroku config:get DATABASE_URL
```

### PostgreSQL on AWS RDS

1. Go to AWS RDS Console
2. Create Database
3. Select PostgreSQL
4. Choose instance size
5. Configure security group
6. Get connection string

### Update Backend

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
flask-sqlalchemy==3.0.5
```

Update `config.py`:
```python
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
```

---

## 🔒 SSL/HTTPS Configuration

### Option 1: Let's Encrypt (Free)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 2: Cloudflare (Free SSL + CDN)

1. Sign up for Cloudflare
2. Add your domain
3. Update nameservers
4. Enable SSL/TLS (Full)
5. Automatic HTTPS rewrites

---

## 📊 Monitoring & Maintenance

### Backend Monitoring

#### 1. Application Logs
```bash
# Heroku
heroku logs --tail

# AWS EC2
sudo journalctl -u puzzle-backend -f

# Local
tail -f logs/app.log
```

#### 2. Performance Monitoring

Add to `requirements.txt`:
```
flask-monitoring-dashboard==3.1.1
```

Add to `app.py`:
```python
from flask_monitoringdashboard import bind
bind(app)
```

#### 3. Error Tracking

**Sentry Integration:**
```bash
pip install sentry-sdk[flask]
```
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Frontend Monitoring

**Google Analytics:**

Add to `public/index.html`:
```html
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. CORS Errors

**Solution:** Update `backend/config.py`:
```python
CORS_ORIGINS = ['https://your-frontend-domain.com']
```

#### 2. TensorFlow/OpenCV Installation Issues

**On Heroku:** Add `Aptfile`:
```
libsm6
libxext6
libxrender-dev
libgomp1
```

**On AWS:** Install system dependencies:
```bash
sudo apt install libgl1-mesa-glx libglib2.0-0
```

#### 3. Out of Memory Errors

**Solutions:**
- Upgrade instance size
- Enable swap on EC2:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. Slow Validation

**Solutions:**
- Enable `FAST_MODE` in config
- Use caching for repeated validations
- Upgrade instance

#### 5. Unsplash API Rate Limits

**Solutions:**
- Cache downloaded images
- Implement rate limiting
- Use fallback images

---

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations complete
- [ ] Security review done
- [ ] Performance testing done
- [ ] SSL certificate configured

### Post-Deployment

- [ ] Verify application is accessible
- [ ] Check all API endpoints
- [ ] Test game functionality
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerts
- [ ] Configure backups
- [ ] Document deployment

---

## 🎯 Production Best Practices

### Security

1. **Never commit secrets** - Use environment variables
2. **Use HTTPS** - Always encrypt traffic
3. **Rate limiting** - Prevent abuse
4. **Input validation** - Sanitize all inputs
5. **CORS** - Restrict origins

### Performance

1. **Caching** - Cache static assets
2. **CDN** - Use CloudFront/Cloudflare
3. **Image optimization** - Compress images
4. **Lazy loading** - Load images on demand
5. **Compression** - Enable gzip

### Reliability

1. **Auto-scaling** - Handle traffic spikes
2. **Health checks** - Monitor uptime
3. **Backups** - Regular database backups
4. **Logging** - Centralized logging
5. **Monitoring** - Track metrics

---

## 🚨 Emergency Procedures

### Rollback Deployment

**Heroku:**
```bash
heroku releases
heroku rollback v123
```

**AWS:**
```bash
git checkout previous-commit
git push origin main --force
```

### Database Recovery
```bash
# Heroku
heroku pg:backups:restore

# AWS RDS
# Use automated snapshots in RDS console
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Search error messages
4. Create GitHub issue
5. Contact support

---

## 🎓 Additional Resources

- [Heroku Python Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)
- [AWS EC2 Tutorial](https://docs.aws.amazon.com/ec2/)
- [Vercel Documentation](https://vercel.com/docs)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt Guide](https://letsencrypt.org/getting-started/)

---

**Good luck with your deployment! 🚀**