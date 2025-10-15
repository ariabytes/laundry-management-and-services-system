import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager


def get_db_connection():
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
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
    finally:
        cursor.close()
