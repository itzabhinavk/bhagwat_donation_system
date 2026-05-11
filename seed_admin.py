"""
seed_admin.py - Create Initial Admin Account
Run this script once after setting up the database to create the admin user.

Usage:
    python seed_admin.py

Make sure your .env file is configured with correct database settings first.
"""
import sys
import os

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from database.db import get_db_connection
from config import Config

def create_admin():
    """Creates the admin user in the database."""

    print("=" * 50)
    print("  Bhagwat System - Admin Account Setup")
    print("=" * 50)

    # Get admin credentials from user
    username = str(input("\nEnter admin username (default: admin): ")).strip()
    if not username:
        username = "admin"

    password = str(input("Enter admin password: ")).strip()
    if not password:
        print("❌ Password cannot be empty!")
        return

    confirm_password = str(input("Confirm password: ")).strip()
    if password != confirm_password:
        print("❌ Passwords do not match!")
        return

    try:
        # Hash the password securely using Werkzeug
        hashed_password = generate_password_hash(password)

        # Connect to database and insert admin
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if admin already exists
        cursor.execute("SELECT id FROM admins WHERE username = %s", (username,))
        existing = cursor.fetchone()

        if existing:
            # Update existing admin password
            cursor.execute(
                "UPDATE admins SET password = %s WHERE username = %s",
                (username, hashed_password)
            )
            print(f"\n✅ Admin '{username}' password updated successfully!")
        else:
            # Insert new admin
            cursor.execute(
                "INSERT INTO admins (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            print(f"\n✅ Admin '{username}' created successfully!")

        cursor.close()
        conn.close()

        print("\nYou can now login at: /admin/login")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure your database is running and .env is configured correctly.")

if __name__ == "__main__":
    create_admin()
