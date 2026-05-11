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
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # MySQL database connection settings (Local MySQL)
    DB_HOST = os.environ.get('DB_HOST', ''),
    DB_USER = os.environ.get('DB_USER', ''),
    DB_PASSWORD = os.environ.get('DB_PASSWORD', ''),
    DB_NAME = os.environ.get('DB_NAME', ''),
    DB_PORT = int(os.environ.get('DB_PORT',),

    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
