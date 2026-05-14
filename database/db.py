"""
database/db.py - MySQL Connection Utility
Provides helpers to create and connect to the MySQL database.
"""
import os
import mysql.connector
from mysql.connector import errorcode, Error
from config import Config



SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


def _initialize_schema(connection):
    """Initialize the database schema from schema.sql."""
    if not os.path.exists(SCHEMA_FILE):
        return

    with open(SCHEMA_FILE, 'r', encoding='utf-8') as schema_file:
        schema_sql = schema_file.read()

    cursor = connection.cursor()
    for _ in cursor.execute(schema_sql, multi=True):
        pass
    cursor.close()


def _create_database_if_missing():
    """Create the database if it does not already exist."""
    server_conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        autocommit=True

        
    )
    try:
        _initialize_schema(server_conn)
    finally:
        server_conn.close()


def _ensure_schema(connection):
    """Ensure the database has the required schema and donation table columns."""
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'donation_tables'",
        (Config.DB_NAME,)
    )
    result = cursor.fetchone()
    donation_tables_exist = result[0] > 0
    
    if not donation_tables_exist:
        _initialize_schema(connection)
        cursor.close()
        return

    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'donations'",
        (Config.DB_NAME,)
    )
    existing_columns = {row[0] for row in cursor.fetchall()}

    if 'donor_contact' not in existing_columns:
        cursor.execute(
            "ALTER TABLE donations ADD COLUMN donor_contact VARCHAR(150) DEFAULT NULL"
        )
    if 'campaign' not in existing_columns:
        cursor.execute(
            "ALTER TABLE donations ADD COLUMN campaign VARCHAR(255) DEFAULT 'General'"
        )
    if 'payment_status' not in existing_columns:
        cursor.execute(
            "ALTER TABLE donations ADD COLUMN payment_status ENUM('Received','Pending','Cancelled') "
            "DEFAULT 'Received'"
        )
    cursor.close()


def get_db_connection():
    """
    Creates and returns a MySQL database connection.
    If the configured database does not exist, it will be created automatically.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            autocommit=True
        )
        _ensure_schema(connection)
        return connection
    except Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            _create_database_if_missing()
            return mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                autocommit=True
            )
        raise RuntimeError(
            f"MySQL connection failed. Ensure MySQL is running and .env values are correct. Original error: {err}"
        )


# ============================================================
# LEDGER HELPER FUNCTIONS
# ============================================================

def get_ledger_summary():
    """
    Get summary of total income, total expenses, and net balance.
    Returns dict with: total_income, total_expenses, net_balance
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get total income (positive payment_status)
    cursor.execute("SELECT COALESCE(SUM(CASE WHEN payment_status > 0 THEN payment_status ELSE 0 END), 0) as total_income FROM expense_ledger")
    income_result = cursor.fetchone()
    total_income = income_result['total_income'] if income_result else 0

    # Get total expenses (absolute of negative payment_status)
    cursor.execute("SELECT COALESCE(SUM(CASE WHEN payment_status < 0 THEN ABS(payment_status) ELSE 0 END), 0) as total_expenses FROM expense_ledger")
    expense_result = cursor.fetchone()
    total_expenses = expense_result['total_expenses'] if expense_result else 0

    # Get current balance (last balance)
    cursor.execute("SELECT balance FROM expense_ledger ORDER BY id DESC LIMIT 1")
    balance_result = cursor.fetchone()
    current_balance = balance_result['balance'] if balance_result else 0

    cursor.close()
    conn.close()

    return {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_balance': float(current_balance)
    }


def get_ledger_entries(page=1, per_page=20, category_filter=None, type_filter=None, date_from=None, date_to=None):
    """
    Get paginated ledger entries with optional filters.
    Returns dict with: entries (list), total_count, total_pages
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Build WHERE clause - but since we removed category and type, adjust filters
    where_conditions = []
    params = []

    # For now, no filters since columns changed
    if date_from:
        where_conditions.append("date >= %s")
        params.append(date_from)

    if date_to:
        where_conditions.append("date <= %s")
        params.append(date_to)

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    # Get total count
    cursor.execute(f"SELECT COUNT(*) as total FROM expense_ledger {where_clause}", params)
    total_count = cursor.fetchone()['total']
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    page = min(max(1, page), total_pages)
    offset = (page - 1) * per_page

    # Get entries
    cursor.execute(f"""
        SELECT id, reason, date, payment_status, balance, created_at, created_by
        FROM expense_ledger
        {where_clause}
        ORDER BY date DESC, created_at DESC
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])

    entries = cursor.fetchall()

    # Format dates and amounts
    for entry in entries:
        entry['date'] = entry['date'].isoformat() if entry['date'] else None
        entry['created_at'] = entry['created_at'].isoformat() if entry['created_at'] else None
        entry['payment_status'] = float(entry['payment_status'])
        entry['balance'] = float(entry['balance'])

    cursor.close()
    conn.close()

    return {
        'entries': entries,
        'total_count': total_count,
        'total_pages': total_pages,
        'current_page': page
    }


def add_ledger_entry(reason, amount, date, created_by, is_income=True):
    """
    Add a new ledger entry.
    amount: positive for income, negative for expense
    Returns the inserted entry ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get current balance
    cursor.execute("SELECT balance FROM expense_ledger ORDER BY id DESC LIMIT 1")
    last_balance = cursor.fetchone()
    current_balance = last_balance['balance'] if last_balance else 0

    new_balance = current_balance + amount

    cursor.execute("""
        INSERT INTO expense_ledger (reason, date, payment_status, balance, created_by)
        VALUES (%s, %s, %s, %s, %s)
    """, (reason, date, amount, new_balance, created_by))

    entry_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return entry_id


def update_ledger_entry(entry_id, reason=None, amount=None, date=None):
    """
    Update an existing ledger entry.
    Only allows updating debit entries (negative payment_status).
    Recalculates balances after update.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if it's a debit entry
    cursor.execute("SELECT payment_status FROM expense_ledger WHERE id = %s", (entry_id,))
    entry = cursor.fetchone()
    if not entry or entry['payment_status'] >= 0:
        cursor.close()
        conn.close()
        return False  # Only debit entries can be edited

    updates = []
    params = []

    if reason is not None:
        updates.append("reason = %s")
        params.append(reason)

    if amount is not None and amount < 0:  # Ensure it's negative
        updates.append("payment_status = %s")
        params.append(amount)

    if date is not None:
        updates.append("date = %s")
        params.append(date)

    if not updates:
        cursor.close()
        conn.close()
        return False

    params.append(entry_id)
    cursor.execute(f"UPDATE expense_ledger SET {', '.join(updates)} WHERE id = %s", params)

    if cursor.rowcount > 0:
        # Recalculate balances from this point
        _recalculate_balances_from(conn, entry_id)
        success = True
    else:
        success = False

    cursor.close()
    conn.close()

    return success


def _recalculate_balances_from(conn, from_id):
    """
    Recalculate balances starting from a given entry ID.
    """
    cursor = conn.cursor()

    # Get all entries from from_id onwards, ordered by id
    cursor.execute("SELECT id, payment_status FROM expense_ledger WHERE id >= %s ORDER BY id", (from_id,))
    entries = cursor.fetchall()

    if not entries:
        return

    # Get balance before from_id
    cursor.execute("SELECT balance FROM expense_ledger WHERE id < %s ORDER BY id DESC LIMIT 1", (from_id,))
    prev_balance_result = cursor.fetchone()
    current_balance = prev_balance_result[0] if prev_balance_result else 0

    # Update each entry's balance
    for entry_id, payment_status in entries:
        current_balance += payment_status
        cursor.execute("UPDATE expense_ledger SET balance = %s WHERE id = %s", (current_balance, entry_id))

    cursor.close()


def delete_ledger_entry(entry_id):
    """
    Delete a ledger entry.
    Recalculates balances after deletion.
    Returns True if deleted, False if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the entry to check if it exists
    cursor.execute("SELECT id FROM expense_ledger WHERE id = %s", (entry_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return False

    cursor.execute("DELETE FROM expense_ledger WHERE id = %s", (entry_id,))
    success = cursor.rowcount > 0

    if success:
        # Recalculate balances from the beginning (simplest way)
        _recalculate_all_balances(conn)

    cursor.close()
    conn.close()

    return success


def _recalculate_all_balances(conn):
    """
    Recalculate all balances in the ledger.
    """
    cursor = conn.cursor()

    # Get all entries ordered by id
    cursor.execute("SELECT id, payment_status FROM expense_ledger ORDER BY id")
    entries = cursor.fetchall()

    current_balance = 0
    for entry_id, payment_status in entries:
        current_balance += payment_status
        cursor.execute("UPDATE expense_ledger SET balance = %s WHERE id = %s", (current_balance, entry_id))

    cursor.close()


def get_ledger_categories():
    """
    Get all unique categories used in the ledger.
    Returns list of category names.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT category FROM expense_ledger ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return categories
