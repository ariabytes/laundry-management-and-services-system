from ..db.connection import get_db_connection, db_cursor


def add_payment_method(payment_method_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "INSERT INTO payment_methods (payment_method_name) VALUES (%s)"
            cursor.execute(sql, (payment_method_name,))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_payment_method_by_id(payment_method_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM payment_methods WHERE payment_method_id = %s"
            cursor.execute(sql, (payment_method_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_payment_methods():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM payment_methods"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_payment_method(payment_method_id, payment_method_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "UPDATE payment_methods SET payment_method_name = %s WHERE payment_method_id = %s"
            cursor.execute(sql, (payment_method_name, payment_method_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_payment_method(payment_method_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM payment_methods WHERE payment_method_id = %s"
            cursor.execute(sql, (payment_method_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
