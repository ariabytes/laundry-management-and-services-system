from db.connection import get_db_connection, db_cursor
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))


def verify_test_order():
    print("🔍 Verifying Test Order in Database...\n")

    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return

    try:
        with db_cursor(conn) as cursor:

            # Check customers
            print("👥 CUSTOMERS:")
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            for customer in customers:
                print(
                    f"   ID: {customer['customer_id']} | {customer['customer_name']} | {customer['customer_phone']}")

            # Check orders
            print(f"\n📋 ORDERS:")
            cursor.execute("""
                SELECT o.order_id, o.customer_id, c.customer_name, o.total_price, 
                       os.order_status_name, o.order_date
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN order_statuses os ON o.order_status_id = os.order_status_id
            """)
            orders = cursor.fetchall()
            for order in orders:
                print(
                    f"   Order ID: {order['order_id']} | Customer: {order['customer_name']} | Total: ₱{order['total_price']} | Status: {order['order_status_name']}")

            # Check order items
            print(f"\n🧼 ORDER ITEMS:")
            cursor.execute("""
                SELECT oi.order_item_id, oi.order_id, s.service_name, oi.quantity, oi.price
                FROM order_items oi
                JOIN services s ON oi.service_id = s.service_id
            """)
            items = cursor.fetchall()
            for item in items:
                print(
                    f"   Item ID: {item['order_item_id']} | Order: {item['order_id']} | {item['quantity']}x {item['service_name']} | ₱{item['price']}")

            # Check payments
            print(f"\n💳 PAYMENTS:")
            cursor.execute("""
                SELECT p.payment_id, p.order_id, p.amount_paid, pm.payment_method_name, 
                       ps.payment_status_name, p.payment_date
                FROM payments p
                JOIN payment_methods pm ON p.payment_method_id = pm.payment_method_id
                JOIN payment_statuses ps ON p.payment_status_id = ps.payment_status_id
            """)
            payments = cursor.fetchall()
            for payment in payments:
                print(
                    f"   Payment ID: {payment['payment_id']} | Order: {payment['order_id']} | Amount: ₱{payment['amount_paid']} | Method: {payment['payment_method_name']} | Status: {payment['payment_status_name']}")

            print(f"\n📊 SUMMARY:")
            print(f"   Total Customers: {len(customers)}")
            print(f"   Total Orders: {len(orders)}")
            print(f"   Total Order Items: {len(items)}")
            print(f"   Total Payments: {len(payments)}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    verify_test_order()
