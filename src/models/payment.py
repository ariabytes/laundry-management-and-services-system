from ..db.connection import get_db_connection, db_cursor


def add_payment(order_id, amount_paid, payment_date, payment_status_id, payment_method_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                INSERT INTO payments (order_id, amount_paid, payment_date, payment_status_id, payment_method_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (order_id, amount_paid,
                           payment_date, payment_status_id, payment_method_id))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_payment_by_id(payment_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM payments WHERE payment_id = %s"
            cursor.execute(sql, (payment_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_payments_by_order(order_id):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM payments WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def update_payment(payment_id, order_id, amount_paid, payment_date, payment_status_id, payment_method_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE payments
                SET order_id = %s, amount_paid = %s, payment_date = %s, payment_status_id = %s, payment_method_id = %s
                WHERE payment_id = %s
            """
            cursor.execute(sql, (order_id, amount_paid, payment_date,
                           payment_status_id, payment_method_id, payment_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_payment(payment_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM payments WHERE payment_id = %s"
            cursor.execute(sql, (payment_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
