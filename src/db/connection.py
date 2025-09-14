import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager


def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.
    Update the config values with your actual database credentials.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",         # Default XAMPP username
            password="",         # Default: blank password
            database="db_laundry"  # Your actual database name
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful!")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


@contextmanager
def db_cursor(conn, dictionary=True):
    """
    Context manager for MySQL cursor.
    Usage:
        with db_cursor(connection) as cursor:
            cursor.execute(...)
    Automatically closes the cursor.
    """
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
    finally:
        cursor.close()
