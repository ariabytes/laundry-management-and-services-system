from src.db.connection import get_db_connection, db_cursor


def add_order_status(order_status_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "INSERT INTO order_statuses (order_status_name) VALUES (%s)"
            cursor.execute(sql, (order_status_name,))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_order_status_by_id(order_status_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM order_statuses WHERE order_status_id = %s"
            cursor.execute(sql, (order_status_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_order_statuses():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM order_statuses"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_order_status(order_status_id, order_status_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "UPDATE order_statuses SET order_status_name = %s WHERE order_status_id = %s"
            cursor.execute(sql, (order_status_name, order_status_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_order_status(order_status_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM order_statuses WHERE order_status_id = %s"
            cursor.execute(sql, (order_status_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
