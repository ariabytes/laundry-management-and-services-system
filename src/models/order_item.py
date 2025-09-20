from src.db.connection import get_db_connection, db_cursor


def add_order_item(order_id, service_id, quantity, price):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                INSERT INTO order_items (order_id, service_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (order_id, service_id, quantity, price))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_order_item_by_id(order_item_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM order_items WHERE order_item_id = %s"
            cursor.execute(sql, (order_item_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_order_items_by_order(order_id):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM order_items WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def update_order_item(order_item_id, order_id, service_id, quantity, price):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE order_items
                SET order_id = %s, service_id = %s, quantity = %s, price = %s
                WHERE order_item_id = %s
            """
            cursor.execute(sql, (order_id, service_id,
                           quantity, price, order_item_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_order_item(order_item_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM order_items WHERE order_item_id = %s"
            cursor.execute(sql, (order_item_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
