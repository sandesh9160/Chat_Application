#!/usr/bin/env python3
"""
Environment Setup Script for Django Chat Application
This script helps create and manage environment variables
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """Generate a secure Django secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def create_env_file(env_type="local"):
    """Create environment file based on type"""
    
    if env_type == "local":
        env_content = f"""# Django Settings
DEBUG=True
SECRET_KEY={generate_secret_key()}
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# For local PostgreSQL
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb

# For local SQLite (fallback)
# DATABASE_URL=sqlite:///db.sqlite3

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/

# PostgreSQL Connection Details
POSTGRES_DB=chatdb
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=chatpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# WebSocket Configuration
CHANNEL_LAYERS={{"default": {{"BACKEND": "channels.layers.InMemoryChannelLayer"}}}}

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Security Settings
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=SAMEORIGIN
"""
        filename = ".env"
        
    elif env_type == "production":
        env_content = f"""# Django Settings (Production)
DEBUG=False
SECRET_KEY={generate_secret_key()}
ALLOWED_HOSTS=.onrender.com,your-app-name.onrender.com

# Database Configuration (Render will auto-configure)
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/

# WebSocket Configuration
CHANNEL_LAYERS={{"default": {{"BACKEND": "channels.layers.InMemoryChannelLayer"}}}}

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf

# Security Settings (Production)
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=SAMEORIGIN
SECURE_SSL_REDIRECT=True

# Email Configuration (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging Configuration
LOGGING_LEVEL=INFO
"""
        filename = ".env.production"
    
    else:
        print(f"❌ Unknown environment type: {env_type}")
        return False
    
    try:
        with open(filename, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {filename} for {env_type} environment")
        return True
    except Exception as e:
        print(f"❌ Error creating {filename}: {e}")
        return False

def load_env_vars():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env")
    else:
        print("⚠️  No .env file found")

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = [
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Main function"""
    print("🔧 Environment Setup for Django Chat Application")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Create local environment file (.env)")
        print("2. Create production environment file (.env.production)")
        print("3. Load environment variables from .env")
        print("4. Check environment variables")
        print("5. Generate new secret key")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            create_env_file("local")
        elif choice == "2":
            create_env_file("production")
        elif choice == "3":
            load_env_vars()
        elif choice == "4":
            check_env_vars()
        elif choice == "5":
            new_key = generate_secret_key()
            print(f"🔑 New secret key: {new_key}")
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 