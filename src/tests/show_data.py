from connection import get_db_connection, db_cursor  # type: ignore
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))


def show_all_data():
    print("📊 Current Database Data:\n")

    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return

    try:
        with db_cursor(conn) as cursor:
            # Show customers
            print("👥 CUSTOMERS:")
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            if customers:
                for customer in customers:
                    print(
                        f"   ID: {customer['customer_id']} | {customer['customer_name']} | {customer['customer_phone']} | {customer['customer_email']}")
            else:
                print("   No customers found")

            print(
                f"\n📂 CATEGORIES ({cursor.execute('SELECT COUNT(*) FROM categories') or cursor.fetchone()}):")
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()
            for cat in categories:
                print(f"   {cat['category_id']}: {cat['category_name']}")

            print(f"\n📋 ORDERS:")
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            order_count = cursor.fetchone()
            print(f"   Total orders: {order_count['count']}")

            print(f"\n💳 PAYMENTS:")
            cursor.execute("SELECT COUNT(*) as count FROM payments")
            payment_count = cursor.fetchone()
            print(f"   Total payments: {payment_count['count']}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    show_all_data()
