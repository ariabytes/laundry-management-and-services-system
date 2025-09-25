from ..db.connection import get_db_connection, db_cursor


def add_payment_status(payment_status_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "INSERT INTO payment_statuses (payment_status_name) VALUES (%s)"
            cursor.execute(sql, (payment_status_name,))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_payment_status_by_id(payment_status_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM payment_statuses WHERE payment_status_id = %s"
            cursor.execute(sql, (payment_status_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_payment_statuses():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM payment_statuses"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_payment_status(payment_status_id, payment_status_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "UPDATE payment_statuses SET payment_status_name = %s WHERE payment_status_id = %s"
            cursor.execute(sql, (payment_status_name, payment_status_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_payment_status(payment_status_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM payment_statuses WHERE payment_status_id = %s"
            cursor.execute(sql, (payment_status_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
