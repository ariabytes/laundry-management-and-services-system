from src.db.connection import get_db_connection, db_cursor
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import using the full path from project root


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

            # Count categories
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            cat_count = cursor.fetchone()
            print(f"\n📂 CATEGORIES (Total: {cat_count['count']}):")
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()
            for cat in categories:
                print(f"   {cat['category_id']}: {cat['category_name']}")

            print("\n📋 ORDERS:")
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            order_count = cursor.fetchone()
            print(f"   Total orders: {order_count['count']}")

            print("\n💳 PAYMENTS:")
            cursor.execute("SELECT COUNT(*) as count FROM payments")
            payment_count = cursor.fetchone()
            print(f"   Total payments: {payment_count['count']}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    show_all_data()
