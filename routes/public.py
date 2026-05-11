"""
routes/public.py - Public Routes Blueprint
Handles all public-facing pages (no login required).
"""
from flask import Blueprint, render_template, request, jsonify
from database.db import get_db_connection

# Create a Blueprint named 'public'
public_bp = Blueprint('public', __name__)


def _fetch_table_metadata(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT table_key, title, description FROM donation_tables ORDER BY id")
    tables = cursor.fetchall()
    cursor.close()
    return tables


def _get_selected_table(table_key, tables):
    if not tables:
        return None
    if table_key:
        for table in tables:
            if table['table_key'] == table_key:
                return table
    return tables[0]


@public_bp.route('/')
def index():
    """
    Homepage - Shows donation table and notices.
    Supports: search, sort, pagination via query parameters.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # --- Query Parameters ---
        search = request.args.get('search', '').strip()
        table_key = request.args.get('table', '').strip()
        sort_by = request.args.get('sort', 'donated_at')
        sort_order = request.args.get('order', 'desc')
        page = int(request.args.get('page', 1))
        per_page = 15  # Records per page

        tables = _fetch_table_metadata(conn)
        selected_table = _get_selected_table(table_key, tables)
        active_table_name = selected_table['table_key'] if selected_table else 'donations'

        # Whitelist allowed sort columns to prevent SQL injection
        allowed_sort_columns = ['donor_name', 'village', 'donor_contact', 'amount', 'payment_method', 'payment_status', 'donated_at']
        if sort_by not in allowed_sort_columns:
            sort_by = 'donated_at'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'

        # --- Build WHERE clause for search ---
        where_clause = ""
        params = []
        if search:
            where_clause = """
                WHERE donor_name LIKE %s
                   OR village LIKE %s
                   OR donor_contact LIKE %s
                   OR payment_method LIKE %s
                   OR payment_status LIKE %s
                   OR remark LIKE %s
            """
            search_term = f"%{search}%"
            params = [search_term, search_term, search_term, search_term, search_term, search_term]

        # --- Get total count for pagination ---
        cursor.execute(f"SELECT COUNT(*) as total FROM {active_table_name} {where_clause}", params)
        total_records = cursor.fetchone()['total']
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = min(max(1, page), total_pages)
        offset = (page - 1) * per_page

        # --- Fetch paginated donations ---
        query = f"""
            SELECT id, donor_name, village, donor_contact, amount, payment_method,
                   payment_status, remark, donated_at
            FROM {active_table_name}
            {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [per_page, offset])
        donations = cursor.fetchall()

        # --- Get total donation sum ---
        cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM {active_table_name} {where_clause}", params)
        total_amount = cursor.fetchone()['total'] or 0

        # --- Get latest 5 notices ---
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC LIMIT 5")
        notices = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('index.html',
            tables=tables,
            selected_table=selected_table,
            donations=donations,
            notices=notices,
            total_amount=total_amount,
            total_records=total_records,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            total_pages=total_pages,
            per_page=per_page
        )

    except Exception as e:
        return render_template('error.html', error=str(e)), 500


@public_bp.route('/notices')
def notices():
    """Shows all notices page."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        notices = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('notices.html', notices=notices)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500
