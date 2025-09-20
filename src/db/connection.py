import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager


def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database using XAMPP.
    - Change host, user, password, and database as needed for your setup.
    - Returns: a MySQL connection object if successful, otherwise None.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",      # XAMPP MySQL server host
            user="root",           # Default XAMPP username
            password="",           # Default: blank password
            database="db_laundry"  # Your actual database name
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful!")
        return connection
    except Error as e:
        # Prints error if connection fails and returns None
        print(f"Error: {e}")
        return None


@contextmanager
def db_cursor(conn, dictionary=True):
    """
    Context manager for MySQL cursor.
    - conn: MySQL connection object.
    - dictionary: If True, cursor returns rows as dictionaries (column names as keys).
        If False, returns rows as tuples.
    - Automatically closes the cursor when done, even if an error occurs.
    """
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
    finally:
        cursor.close()
