# PostgreSQL Setup Guide for Django Chat Application

This guide will help you set up PostgreSQL for your Django chat application.

## Prerequisites

- Python 3.11+
- pip package manager
- Git

## Installation

### Windows

1. **Download PostgreSQL:**
   - Go to https://www.postgresql.org/download/windows/
   - Download the latest version for Windows
   - Run the installer

2. **Installation Steps:**
   - Choose installation directory
   - Set password for `postgres` user (remember this!)
   - Keep default port (5432)
   - Complete installation

3. **Add to PATH:**
   - Add `C:\Program Files\PostgreSQL\[version]\bin` to your system PATH
   - Restart command prompt

### macOS

```bash
# Using Homebrew
brew install postgresql

# Start PostgreSQL service
brew services start postgresql
```

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Database Setup

### Method 1: Using the Setup Script

1. **Run the Python setup script:**
```bash
python postgres_setup.py
```

### Method 2: Manual Setup

1. **Connect to PostgreSQL as superuser:**
```bash
# Windows
psql -U postgres

# macOS/Linux
sudo -u postgres psql
```

2. **Run the SQL script:**
```sql
\i postgres_setup.sql
```

3. **Or run commands manually:**
```sql
-- Create database
CREATE DATABASE chatdb;

-- Create user
CREATE USER chatuser WITH PASSWORD 'chatpassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chatdb TO chatuser;

-- Connect to database
\c chatdb;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO chatuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chatuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chatuser;
```

## Django Configuration

### 1. Install PostgreSQL adapter

```bash
pip install psycopg2-binary
```

### 2. Update settings.py

The settings.py file has been updated to support PostgreSQL. It will automatically use:
- PostgreSQL if `DATABASE_URL` environment variable is set
- Local PostgreSQL configuration if running locally
- SQLite as fallback

### 3. Environment Variables

Create a `.env` file in your project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
```

## Testing the Connection

### 1. Test PostgreSQL connection

```bash
# Connect to database
psql -h localhost -U chatuser -d chatdb
# Enter password: chatpassword
```

### 2. Run Django migrations

```bash
python manage.py migrate
```

### 3. Create superuser

```bash
python manage.py createsuperuser
```

### 4. Run the development server

```bash
python manage.py runserver
```

## Troubleshooting

### Common Issues

1. **Connection refused:**
   - Check if PostgreSQL service is running
   - Verify port 5432 is not blocked
   - Check firewall settings

2. **Authentication failed:**
   - Verify username and password
   - Check pg_hba.conf file
   - Try connecting as postgres user first

3. **Database does not exist:**
   - Run the setup script again
   - Check database name spelling
   - Verify user has proper privileges

### Useful Commands

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# List databases
psql -U postgres -l

# List users
psql -U postgres -c "\du"

# Backup database
pg_dump -U chatuser chatdb > backup.sql

# Restore database
psql -U chatuser chatdb < backup.sql
```

## Production Considerations

### Security

1. **Change default passwords**
2. **Use environment variables for sensitive data**
3. **Limit database access**
4. **Regular backups**

### Performance

1. **Configure connection pooling**
2. **Optimize queries**
3. **Monitor database performance**
4. **Use indexes appropriately**

## Next Steps

After setting up PostgreSQL:

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Create superuser: `python manage.py createsuperuser`
3. ✅ Test the application: `python manage.py runserver`
4. ✅ Deploy to production (Render, Heroku, etc.)

## Support

If you encounter issues:

1. Check PostgreSQL logs
2. Verify Django settings
3. Test database connection manually
4. Check environment variables
5. Review error messages carefully

---

**Note:** This setup is for development. For production, use proper security practices and environment-specific configurations. 