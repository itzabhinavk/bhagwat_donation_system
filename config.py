"""
config.py - Application Configuration
Loads settings from environment variables (.env file)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file into environment
# Explicitly specify the .env file path
env_file = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_file, override=True)

class Config:
    # Flask secret key for session management
    SECRET_KEY = str(os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production')

    # MySQL database connection settings (Local MySQL)
      DB_HOST = str(os.environ.get('DB_HOST') or 'localhost')
    DB_USER = str(os.environ.get('DB_USER') or 'root')
    DB_PASSWORD = str(os.environ.get('DB_PASSWORD') or 'Shubham#1204')
    DB_NAME = str(os.environ.get('DB_NAME') or 'bhagwat_db')
    DB_PORT = int(str(os.environ.get('DB_PORT') or '3306'))

    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
