from db.connection import get_db_connection, db_cursor


def add_customer(name, phone, email, address):
    """
    Add a new customer to the database.
    """
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
    """
    Retrieve a customer by ID.
    Aliases are used so GUI keys match ('contact_number', 'email', 'address').
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with db_cursor(conn) as cursor:
            sql = """
                SELECT
                    customer_id,
                    customer_name,
                    customer_phone AS contact_number,
                    customer_email AS email,
                    customer_address AS address
                FROM customers
                WHERE customer_id = %s
            """
            cursor.execute(sql, (customer_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_all_customers():
    """
    Retrieve all customers from the database.
    Aliases match GUI keys for consistency.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with db_cursor(conn) as cursor:
            sql = """
                SELECT
                    customer_id,
                    customer_name,
                    customer_phone AS contact_number,
                    customer_email AS email,
                    customer_address AS address
                FROM customers
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def update_customer(customer_id, name, phone, email, address):
    """
    Update an existing customer's information.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with db_cursor(conn) as cursor:
            sql = """
                UPDATE customers
                SET
                    customer_name = %s,
                    customer_phone = %s,
                    customer_email = %s,
                    customer_address = %s
                WHERE customer_id = %s
            """
            cursor.execute(sql, (name, phone, email, address, customer_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_customer(customer_id):
    """
    Delete a customer by ID.
    """
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
