from src.db.connection import get_db_connection, db_cursor


def add_service(category_id, service_name, min_price, max_price, price_unit, service_notes):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                INSERT INTO services (category_id, service_name, min_price, max_price, price_unit, service_notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (category_id, service_name,
                           min_price, max_price, price_unit, service_notes))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_service_by_id(service_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM services WHERE service_id = %s"
            cursor.execute(sql, (service_id,))
            row = cursor.fetchone()
            if row:
                return row  # Already a dict!
            return None
    finally:
        conn.close()


def get_all_services():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM services"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows  # Already a list of dicts!
    finally:
        conn.close()


def update_service(service_id, category_id, service_name, min_price, max_price, price_unit, service_notes):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE services
                SET category_id=%s, service_name=%s, min_price=%s, max_price=%s, price_unit=%s, service_notes=%s
                WHERE service_id=%s
            """
            cursor.execute(sql, (category_id, service_name, min_price,
                           max_price, price_unit, service_notes, service_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_service(service_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM services WHERE service_id=%s"
            cursor.execute(sql, (service_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
