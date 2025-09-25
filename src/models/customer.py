from ..db.connection import get_db_connection, db_cursor


def add_customer(name, phone, email, address):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                INSERT INTO customers (customer_name, customer_phone, customer_email, customer_address)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, phone, email, address))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_customer_by_id(customer_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM customers WHERE customer_id = %s"
            cursor.execute(sql, (customer_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_customers():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM customers"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_customer(customer_id, name, phone, email, address):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE customers
                SET customer_name = %s, customer_phone = %s, customer_email = %s, customer_address = %s
                WHERE customer_id = %s
            """
            cursor.execute(sql, (name, phone, email, address, customer_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_customer(customer_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM customers WHERE customer_id = %s"
            cursor.execute(sql, (customer_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
