from ..db.connection import get_db_connection, db_cursor


def add_order(customer_id, order_status_id, order_date, total_price):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                INSERT INTO orders (customer_id, order_status_id, order_date, total_price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                sql, (customer_id, order_status_id, order_date, total_price))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_order_by_id(order_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM orders WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_orders():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM orders"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_order(order_id, customer_id, order_status_id, order_date, total_price):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE orders
                SET customer_id = %s, order_status_id = %s, order_date = %s, total_price = %s
                WHERE order_id = %s
            """
            cursor.execute(sql, (customer_id, order_status_id,
                           order_date, total_price, order_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_order(order_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM orders WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
