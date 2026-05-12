"""
utils/helpers.py - Shared Helper Utilities
Contains reusable functions used across routes.
"""
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash
from database.db import get_db_connection


def _row_to_dict(cursor, row):
    """Convert a tuple row to a dict if cursor returned non-dictionary rows."""
    if row is None or isinstance(row, dict):
        return row
    if hasattr(cursor, 'column_names'):
        return dict(zip(cursor.column_names, row))
    return row

def generate_session_token():
    """Generate a unique session token."""
    return str(uuid.uuid4())


def login_required(f):
    """
    Decorator: Protects admin routes.
    Checks if admin is logged in and session is valid.
    If not, redirects to login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin_id is in session
        if 'admin_id' not in session:
            flash('Please login to access admin panel.', 'error')
            return redirect(url_for('admin.login'))

        # Verify this session is still the active session in DB
        # (Prevents multiple simultaneous sessions)
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT active_session FROM admins WHERE id = %s",
                (session['admin_id'],)
            )
            admin = cursor.fetchone()
            cursor.close()
            conn.close()

            if not admin or admin['active_session'] != session.get('session_token'):
                # Session was invalidated (another login happened)
                session.clear()
                flash('Your session was ended. Another device logged in.', 'error')
                return redirect(url_for('admin.login'))

        except Exception:
            session.clear()
            return redirect(url_for('admin.login'))

        return f(*args, **kwargs)
    return decorated_function


def generate_session_token():
    """Generates a unique session token for single-session enforcement."""
    return str(uuid.uuid4())


def format_amount(amount):
    """Formats a number as Indian currency style (e.g., 1,00,000)."""
    try:
        return f"₹{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"
