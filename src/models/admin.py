from db.connection import get_db_connection, db_cursor


def add_admin(username, email, password, created_at, name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                INSERT INTO admin (username, email, password, created_at, name)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (username, email, password, created_at, name))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_admin_by_id(admin_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM admin WHERE admin_id = %s"
            cursor.execute(sql, (admin_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_admin_by_username(username):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = "SELECT * FROM admin WHERE username = %s"
            cursor.execute(sql, (username,))
            return cursor.fetchone()
    finally:
        conn.close()


def update_admin(admin_id, username, email, password, name):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE admin
                SET username = %s, email = %s, password = %s, name = %s
                WHERE admin_id = %s
            """
            cursor.execute(sql, (username, email, password, name, admin_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_admin(admin_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = "DELETE FROM admin WHERE admin_id = %s"
            cursor.execute(sql, (admin_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
