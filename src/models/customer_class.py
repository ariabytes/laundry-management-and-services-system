from db.connection import get_db_connection, db_cursor


class Customer:
    """Customer model class - represents a customer entity"""

    def __init__(self, customer_id=None, name="", phone="", email="", address=""):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address

    def save(self):
        """Save customer to database (insert or update)"""
        conn = get_db_connection()
        if not conn:
            return False
        try:
            with db_cursor(conn) as cursor:
                if self.customer_id:
                    # Update existing
                    sql = """
                        UPDATE customers
                        SET customer_name = %s, customer_phone = %s, 
                            customer_email = %s, customer_address = %s
                        WHERE customer_id = %s
                    """
                    cursor.execute(sql, (self.name, self.phone, self.email,
                                         self.address, self.customer_id))
                else:
                    # Insert new
                    sql = """
                        INSERT INTO customers 
                        (customer_name, customer_phone, customer_email, customer_address)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (self.name, self.phone,
                                   self.email, self.address))
                    self.customer_id = cursor.lastrowid
                conn.commit()
                return True
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, customer_id):
        """Load customer from database by ID"""
        conn = get_db_connection()
        if not conn:
            return None
        try:
            with db_cursor(conn) as cursor:
                sql = """
                    SELECT customer_id, customer_name, 
                           customer_phone AS contact_number,
                           customer_email AS email,
                           customer_address AS address
                    FROM customers WHERE customer_id = %s
                """
                cursor.execute(sql, (customer_id,))
                row = cursor.fetchone()
                if row:
                    return cls(
                        customer_id=row['customer_id'],
                        name=row.get('customer_name', ''),
                        phone=row.get('contact_number', ''),
                        email=row.get('email', ''),
                        address=row.get('address', '')
                    )
                return None
        finally:
            conn.close()

    @classmethod
    def get_all(cls):
        """Get all customers from database"""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            with db_cursor(conn) as cursor:
                sql = """
                    SELECT customer_id, customer_name,
                           customer_phone AS contact_number,
                           customer_email AS email,
                           customer_address AS address
                    FROM customers
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [cls(
                    customer_id=r['customer_id'],
                    name=r.get('customer_name', ''),
                    phone=r.get('contact_number', ''),
                    email=r.get('email', ''),
                    address=r.get('address', '')
                ) for r in rows]
        finally:
            conn.close()

    def delete(self):
        """Delete this customer from database"""
        if not self.customer_id:
            return False
        conn = get_db_connection()
        if not conn:
            return False
        try:
            with db_cursor(conn) as cursor:
                sql = "DELETE FROM customers WHERE customer_id = %s"
                cursor.execute(sql, (self.customer_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    def is_valid(self):
        """Validate customer data"""
        return bool(self.name and self.phone)

    def to_dict(self):
        """Convert to dictionary for compatibility with old code"""
        return {
            'customer_id': self.customer_id,
            'customer_name': self.name,
            'contact_number': self.phone,
            'email': self.email,
            'address': self.address
        }


# Keep old functions for backward compatibility (so you don't break existing code)
def add_customer(name, phone, email, address):
    customer = Customer(name=name, phone=phone, email=email, address=address)
    if customer.save():
        return customer.customer_id
    return False


def get_customer_by_id(customer_id):
    customer = Customer.get_by_id(customer_id)
    return customer.to_dict() if customer else None


def get_all_customers():
    customers = Customer.get_all()
    return [c.to_dict() for c in customers]


def update_customer(customer_id, name, phone, email, address):
    customer = Customer(customer_id=customer_id, name=name, phone=phone,
                        email=email, address=address)
    return customer.save()


def delete_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    return customer.delete() if customer else False
