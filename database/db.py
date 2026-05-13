"""
database/db.py - MySQL Connection Utility
Provides helpers to create and connect to the MySQL database.
"""
import os
import pymysql
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
    server_conn = pymysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        autocommit=True,
        cursorclass=pymysql.curors.DictDictCursor
        
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
    donation_tables_exist = cursor.fetchone()[0] > 0

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
        connection =pymysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            autocommit=True,
            cursorclass=pymysql.curors.DictDictCursor
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
