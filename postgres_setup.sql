-- PostgreSQL Setup Script for Django Chat Application
-- Run this script as a PostgreSQL superuser (usually 'postgres')

-- Create database
CREATE DATABASE chatdb;

-- Create user
CREATE USER chatuser WITH PASSWORD 'chatpassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chatdb TO chatuser;

-- Connect to the database
\c chatdb;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO chatuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chatuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chatuser;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO chatuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO chatuser;

-- Verify setup
SELECT 'Database setup completed successfully!' as status; 