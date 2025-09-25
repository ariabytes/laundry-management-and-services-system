from ..db.connection import get_db_connection, db_cursor


def add_category(category_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "INSERT INTO categories (category_name) VALUES (%s)"
            cursor.execute(sql, (category_name,))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_category_by_id(category_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM categories WHERE category_id = %s"
            cursor.execute(sql, (category_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_categories():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM categories"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_category(category_id, category_name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "UPDATE categories SET category_name = %s WHERE category_id = %s"
            cursor.execute(sql, (category_name, category_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_category(category_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM categories WHERE category_id = %s"
            cursor.execute(sql, (category_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
