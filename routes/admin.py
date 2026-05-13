"""
routes/admin.py - Admin Routes Blueprint
Handles all admin panel pages (login required for most routes).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime
from database.db import get_db_connection
from utils.helpers import login_required, generate_session_token
import pymysql

# Create Blueprint named 'admin'
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _fetch_table_metadata(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT table_key, title, description FROM donation_tables ORDER BY id")
    tables = cursor.fetchall()
    cursor.close()
    return tables


def _get_selected_table(table_key, tables):
    if not tables:
        return None
    keys = {t['table_key'] for t in tables}
    if table_key in keys:
        return next((t for t in tables if t['table_key'] == table_key), tables[0])
    return tables[0]


def _table_exists(table_key, tables):
    return any(t['table_key'] == table_key for t in tables)


# ============================================================
# LOGIN / LOGOUT
# ============================================================

@admin_bp.route('/')
def admin_root():
    """Redirect /admin to login or dashboard."""
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    # If already logged in, go to dashboard
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = str(request.form.get('username', '')).strip()
        password = str(request.form.get('password', '')).strip()

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('admin/login.html')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # Find admin by username
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()

            if admin and check_password_hash(admin['password'], password):
                # Generate new session token (invalidates any previous sessions)
                new_token = generate_session_token()

                # Update active_session in DB - this kicks out any other logged-in session
                cursor.execute(
                    "UPDATE admins SET active_session = %s WHERE id = %s",
                    (new_token, admin['id'])
                )

                cursor.close()
                conn.close()

                # Store in Flask session
                session.clear()
                session['admin_id'] = admin['id']
                session['admin_username'] = admin['username']
                session['session_token'] = new_token
                session.permanent = True

                flash('Welcome back! You are now logged in.', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                cursor.close()
                conn.close()
                flash('Invalid username or password.', 'error')

        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Logs out admin and invalidates their session in DB."""
    if 'admin_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Clear active session in database
            cursor.execute(
                "UPDATE admins SET active_session = NULL WHERE id = %s",
                (session['admin_id'],)
            )
            cursor.close()
            conn.close()
        except Exception:
            pass

    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))


# ============================================================
# DASHBOARD
# ============================================================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Main admin dashboard with stats and management."""
    table_key = str(request.args.get('table', '')).strip()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)

        total_donations_count = 0
        total_amount = 0
        pending_donations = 0

        for table in tables:
            cursor.execute(
                f"SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM {table['table_key']}"
            )
            summary = cursor.fetchone()
            table['count'] = summary['count']
            table['total'] = summary['total'] or 0
            total_donations_count += table['count']
            total_amount += table['total']

            cursor.execute(
                f"SELECT COUNT(*) AS count FROM {table['table_key']} WHERE payment_status = 'Pending'"
            )
            table['pending_count'] = cursor.fetchone()['count']
            pending_donations += table['pending_count']

        page_str = str(request.args.get('page', '1')).strip()
        page = int(page_str) if page_str.isdigit() else 1
        per_page = 20
        cursor.execute(
            f"SELECT COUNT(*) AS total FROM {selected_table['table_key']}"
        )
        total_records = cursor.fetchone()['total']
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = min(max(1, page), total_pages)
        offset = (page - 1) * per_page

        cursor.execute(f"""
            SELECT id, donor_name, village, donor_contact, amount,
                   payment_method, payment_status, remark, donated_at
            FROM {selected_table['table_key']}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        donations = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as count FROM notices")
        total_notices = cursor.fetchone()['count']

        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        notices = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('admin/dashboard.html',
            tables=tables,
            selected_table=selected_table,
            total_donations_count=total_donations_count,
            total_amount=total_amount,
            pending_donations=pending_donations,
            total_notices=total_notices,
            donations=donations,
            notices=notices,
            page=page,
            total_pages=total_pages,
            total_records=total_records,
            now=datetime.now()
        )

    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html',
            tables=[],
            selected_table=None,
            total_donations_count=0,
            total_amount=0,
            pending_donations=0,
            total_notices=0,
            donations=[],
            notices=[],
            page=1,
            total_pages=1,
            total_records=0
        )


# ============================================================
# DONATION CRUD
# ============================================================

@admin_bp.route('/add-donation', methods=['POST'])
@login_required
def add_donation():
    """Add a new donation record."""
    table_key = str(request.form.get('table_key', '')).strip()
    donor_name = str(request.form.get('donor_name', '')).strip()
    village = str(request.form.get('village', '')).strip()
    donor_contact = str(request.form.get('donor_contact', '')).strip()
    amount = str(request.form.get('amount', '')).strip()
    payment_method = str(request.form.get('payment_method', 'Cash')).strip()
    payment_status = str(request.form.get('payment_status', 'Received')).strip()
    remark = str(request.form.get('remark', '')).strip()
    donated_at = str(request.form.get('donated_at', '')).strip()

    try:
        conn = get_db_connection()
        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)
        conn.close()
    except Exception:
        selected_table = None

    if not selected_table:
        flash('Selected table is not available.', 'error')
        return redirect(url_for('admin.dashboard'))

    if not all([donor_name, village, amount, donated_at]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('admin.dashboard', table=selected_table['table_key']))

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        flash('Please enter a valid donation amount.', 'error')
        return redirect(url_for('admin.dashboard', table=selected_table['table_key']))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {selected_table['table_key']} (
                donor_name, village, donor_contact,
                amount, payment_method, payment_status,
                remark, donated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            donor_name,
            village,
            donor_contact or None,
            amount_val,
            payment_method,
            payment_status,
            remark or None,
            donated_at
        ))
        cursor.close()
        conn.close()
        flash(f"Donation added to {selected_table['title']} successfully!", 'success')
    except Exception as e:
        flash(f'Error adding donation: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard', table=selected_table['table_key']))


@admin_bp.route('/get-donation/<string:table_key>/<int:donation_id>')
@login_required
def get_donation(table_key, donation_id):
    """Get a single donation record as JSON (for edit modal)."""
    try:
        conn = get_db_connection()
        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)
        if not selected_table:
            return jsonify({'error': 'Invalid table selected'}), 404

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f"SELECT * FROM {selected_table['table_key']} WHERE id = %s",
            (donation_id,)
        )
        donation = cursor.fetchone()
        cursor.close()
        conn.close()

        if not donation:
            return jsonify({'error': 'Donation not found'}), 404

        donation['donated_at'] = str(donation['donated_at'])
        donation['created_at'] = str(donation['created_at'])
        donation['amount'] = float(donation['amount'])
        return jsonify(donation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/edit-donation/<string:table_key>/<int:donation_id>', methods=['POST'])
@login_required
def edit_donation(table_key, donation_id):
    """Update an existing donation record."""
    donor_name = str(request.form.get('donor_name', '')).strip()
    village = str(request.form.get('village', '')).strip()
    donor_contact = str(request.form.get('donor_contact', '')).strip()
    amount = str(request.form.get('amount', '')).strip()
    payment_method = str(request.form.get('payment_method', 'Cash')).strip()
    payment_status = str(request.form.get('payment_status', 'Received')).strip()
    remark = str(request.form.get('remark', '')).strip()
    donated_at = str(request.form.get('donated_at', '')).strip()

    try:
        conn = get_db_connection()
        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)
        conn.close()
    except Exception:
        selected_table = None

    if not selected_table:
        flash('Selected table is not available.', 'error')
        return redirect(url_for('admin.dashboard'))

    if not all([donor_name, village, amount, donated_at]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('admin.dashboard', table=selected_table['table_key']))

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError()
    except ValueError:
        flash('Please enter a valid donation amount.', 'error')
        return redirect(url_for('admin.dashboard', table=selected_table['table_key']))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE {selected_table['table_key']}
            SET donor_name=%s,
                village=%s,
                donor_contact=%s,
                amount=%s,
                payment_method=%s,
                payment_status=%s,
                remark=%s,
                donated_at=%s
            WHERE id=%s
        """, (
            donor_name,
            village,
            donor_contact or None,
            amount_val,
            payment_method,
            payment_status,
            remark or None,
            donated_at,
            donation_id
        ))
        cursor.close()
        conn.close()
        flash('Donation updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating donation: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard', table=selected_table['table_key']))


@admin_bp.route('/delete-donation/<string:table_key>/<int:donation_id>', methods=['POST'])
@login_required
def delete_donation(table_key, donation_id):
    """Delete a donation record."""
    try:
        conn = get_db_connection()
        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)
        if not selected_table:
            flash('Selected table is not available.', 'error')
            return redirect(url_for('admin.dashboard'))

        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM {selected_table['table_key']} WHERE id = %s",
            (donation_id,)
        )
        cursor.close()
        conn.close()
        flash('Donation deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting donation: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard', table=selected_table['table_key']))


@admin_bp.route('/update-table-meta/<string:table_key>', methods=['POST'])
@login_required
def update_table_meta(table_key):
    """Update the selected donation table title and description."""
    title = str(request.form.get('title', '')).strip()
    description = str(request.form.get('description', '')).strip()

    try:
        conn = get_db_connection()
        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)
        if not selected_table:
            flash('Selected table is not available.', 'error')
            return redirect(url_for('admin.dashboard'))

        if not title:
            flash('Table title cannot be empty.', 'error')
            return redirect(url_for('admin.dashboard', table=selected_table['table_key']))

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE donation_tables SET title=%s, description=%s WHERE table_key=%s",
            (title, description or None, selected_table['table_key'])
        )
        cursor.close()
        conn.commit()
        conn.close()
        flash('Table heading updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating table heading: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard', table=selected_table['table_key']))


# ============================================================
# NOTICE CRUD
# ============================================================

@admin_bp.route('/add-notice', methods=['POST'])
@login_required
def add_notice():
    """Add a new notice."""
    title = str(request.form.get('title', '')).strip()
    message = str(request.form.get('message', '')).strip()

    if not title or not message:
        flash('Please fill in both title and message for the notice.', 'error')
        return redirect(url_for('admin.dashboard') + '#notices')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notices (title, message) VALUES (%s, %s)", (title, message))
        cursor.close()
        conn.close()
        flash('Notice added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding notice: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard') + '#notices-section')


@admin_bp.route('/get-notice/<int:notice_id>')
@login_required
def get_notice(notice_id):
    """Get a single notice as JSON (for edit modal)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notices WHERE id = %s", (notice_id,))
        notice = cursor.fetchone()
        cursor.close()
        conn.close()

        if not notice:
            return jsonify({'error': 'Notice not found'}), 404

        notice['created_at'] = str(notice['created_at'])
        return jsonify(notice)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/edit-notice/<int:notice_id>', methods=['POST'])
@login_required
def edit_notice(notice_id):
    """Update a notice."""
    title = str(request.form.get('title', '')).strip()
    message = str(request.form.get('message', '')).strip()

    if not title or not message:
        flash('Please fill in both title and message.', 'error')
        return redirect(url_for('admin.dashboard') + '#notices-section')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notices SET title=%s, message=%s WHERE id=%s",
            (title, message, notice_id)
        )
        cursor.close()
        conn.close()
        flash('Notice updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating notice: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard') + '#notices-section')


@admin_bp.route('/delete-notice/<int:notice_id>', methods=['POST'])
@login_required
def delete_notice(notice_id):
    """Delete a notice."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
        cursor.close()
        conn.close()
        flash('Notice deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting notice: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard') + '#notices-section')
