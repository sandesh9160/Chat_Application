#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Django Chat Application
This script helps set up PostgreSQL database for local development
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_postgres_installation():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed or not in PATH")
        return False

def create_database():
    """Create PostgreSQL database"""
    db_name = "chatdb"
    db_user = "chatuser"
    db_password = "chatpassword"
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="postgres"  # Default password, change if different
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_user WHERE usename = %s", (db_user,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            # Create user
            cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            print(f"✅ User '{db_user}' created successfully")
        else:
            print(f"✅ User '{db_user}' already exists")
        
        # Grant privileges
        cursor.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO {db_user}')
        print(f"✅ Privileges granted to '{db_user}' on '{db_name}'")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_env_file():
    """Create .env file with database configuration"""
    env_content = """# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-n%l*@n43h!dze14ry5(9rmf=&7gtf_^bx4x=!$r!$#d5e@$g6(
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def update_settings_for_postgres():
    """Update settings.py to use PostgreSQL"""
    settings_file = "django_chat/settings.py"
    
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Check if PostgreSQL configuration already exists
        if "postgresql://" in content:
            print("✅ PostgreSQL configuration already exists in settings.py")
            return True
        
        # Add PostgreSQL configuration
        postgres_config = '''
# PostgreSQL Database Configuration
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Local PostgreSQL configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'chatdb',
            'USER': 'chatuser',
            'PASSWORD': 'chatpassword',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
'''
        
        # Replace the existing DATABASES configuration
        import re
        pattern = r'DATABASES\s*=\s*\{[^}]*\}'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, postgres_config.strip(), content, flags=re.DOTALL)
        else:
            # If no DATABASES found, add it after the imports
            content = content.replace('import os\nimport dj_database_url\nfrom pathlib import Path', 
                                    'import os\nimport dj_database_url\nfrom pathlib import Path\n' + postgres_config)
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("✅ settings.py updated for PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Error updating settings.py: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PostgreSQL Setup for Django Chat Application")
    print("=" * 50)
    
    # Check PostgreSQL installation
    if not check_postgres_installation():
        print("\n📋 Please install PostgreSQL first:")
        print("   Windows: Download from https://www.postgresql.org/download/windows/")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return
    
    # Create database and user
    if not create_database():
        print("\n❌ Failed to create database. Please check PostgreSQL installation.")
        return
    
    # Create .env file
    if not create_env_file():
        print("\n❌ Failed to create .env file.")
        return
    
    # Update settings.py
    if not update_settings_for_postgres():
        print("\n❌ Failed to update settings.py.")
        return
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run: python manage.py migrate")
    print("   2. Run: python manage.py createsuperuser")
    print("   3. Run: python manage.py runserver")
    print("\n🔗 Database connection:")
    print("   Host: localhost")
    print("   Port: 5432")
    print("   Database: chatdb")
    print("   User: chatuser")
    print("   Password: chatpassword")

if __name__ == "__main__":
    main() 