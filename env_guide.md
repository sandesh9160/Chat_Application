# Environment Variables Guide

This guide explains how to set up and manage environment variables for your Django chat application.

## 📁 Environment Files

### 1. **`env_local.txt`** - Local Development
- Contains all variables for local development
- Copy to `.env` for local use
- Includes PostgreSQL and SQLite configurations

### 2. **`env_production.txt`** - Production Settings
- Secure settings for production deployment
- Used for Render deployment
- Includes HTTPS and security settings

### 3. **`env_setup.py`** - Interactive Setup Script
- Interactive script to create environment files
- Generates secure secret keys
- Validates environment configuration

## 🚀 Quick Setup

### Option 1: Manual Setup

1. **Copy the local environment file:**
```bash
cp env_local.txt .env
```

2. **Edit `.env` file with your settings:**
```bash
# Edit the file with your preferred editor
nano .env
# or
code .env
```

### Option 2: Interactive Setup

1. **Run the setup script:**
```bash
python env_setup.py
```

2. **Choose option 1** to create local environment file

## 🔧 Environment Variables Explained

### Core Django Settings

```env
# Django Settings
DEBUG=True                    # Set to False in production
SECRET_KEY=your-secret-key    # Auto-generated secure key
ALLOWED_HOSTS=localhost,127.0.0.1  # Comma-separated hosts
```

### Database Configuration

```env
# PostgreSQL (recommended)
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb

# SQLite (fallback)
DATABASE_URL=sqlite:///db.sqlite3

# Individual PostgreSQL settings
POSTGRES_DB=chatdb
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=chatpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### WebSocket Configuration

```env
# In-memory channel layer (for single instance)
CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Redis channel layer (for multiple instances)
# CHANNEL_LAYERS={"default": {"BACKEND": "channels_redis.core.RedisChannelLayer", "CONFIG": {"hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')]}}}
```

### File Upload Settings

```env
MAX_UPLOAD_SIZE=10485760      # 10MB in bytes
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf
```

### Security Settings

```env
# Development
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# Production
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

## 🌍 Environment-Specific Configurations

### Local Development

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
```

### Production (Render)

```env
DEBUG=False
ALLOWED_HOSTS=.onrender.com,your-app-name.onrender.com
DATABASE_URL=postgresql://...  # Auto-configured by Render
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

## 🔐 Security Best Practices

### 1. **Secret Key Management**
- Never commit `.env` files to version control
- Use different secret keys for each environment
- Generate secure keys using the setup script

### 2. **Database Security**
- Use strong passwords
- Limit database access
- Use environment variables for credentials

### 3. **Production Security**
- Set `DEBUG=False`
- Enable HTTPS
- Use secure cookies
- Validate file uploads

## 🛠️ Troubleshooting

### Common Issues

1. **Environment variables not loading:**
```bash
# Check if .env file exists
ls -la .env

# Verify file permissions
chmod 600 .env

# Test loading
python env_setup.py
# Choose option 3: Load environment variables
```

2. **Database connection issues:**
```bash
# Test PostgreSQL connection
psql -h localhost -U chatuser -d chatdb

# Check environment variables
python env_setup.py
# Choose option 4: Check environment variables
```

3. **Secret key issues:**
```bash
# Generate new secret key
python env_setup.py
# Choose option 5: Generate new secret key
```

### Validation Commands

```bash
# Check if all required variables are set
python env_setup.py
# Choose option 4

# Test Django settings
python manage.py check

# Test database connection
python manage.py dbshell
```

## 📋 Environment Checklist

### Local Development
- [ ] `.env` file created
- [ ] `SECRET_KEY` set
- [ ] `DEBUG=True`
- [ ] Database URL configured
- [ ] Allowed hosts set
- [ ] File upload settings configured

### Production (Render)
- [ ] Environment variables set in Render dashboard
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` auto-generated
- [ ] `ALLOWED_HOSTS` includes `.onrender.com`
- [ ] `DATABASE_URL` auto-configured
- [ ] Security settings enabled

## 🔄 Environment Management

### Using the Setup Script

```bash
python env_setup.py
```

**Available options:**
1. Create local environment file (.env)
2. Create production environment file (.env.production)
3. Load environment variables from .env
4. Check environment variables
5. Generate new secret key
6. Exit

### Manual Management

```bash
# Create .env file
cp env_local.txt .env

# Edit environment variables
nano .env

# Load variables (if not using python-dotenv)
export $(cat .env | xargs)
```

## 📚 Additional Resources

- [Django Environment Variables](https://docs.djangoproject.com/en/stable/topics/settings/)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Render Environment Variables](https://render.com/docs/environment-variables)

---

**Remember:** Never commit sensitive information like secret keys or database passwords to version control! 