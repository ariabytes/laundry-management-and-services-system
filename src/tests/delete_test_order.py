from db.connection import get_db_connection, db_cursor
import sys
import os
import json

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))


def delete_test_order():
    """
    Delete the test order created by add_test_order.py
    This will remove:
    1. Payment record
    2. Order items
    3. Order
    4. Customer
    """
    print("🗑️  Deleting Test Order Data...\n")

    # Try to load order data from file
    try:
        with open('last_test_order.json', 'r') as f:
            order_data = json.load(f)
        print("📂 Loaded order data from 'last_test_order.json'")
    except FileNotFoundError:
        print("❌ No 'last_test_order.json' file found!")
        print("💡 Run 'add_test_order.py' first to create test data")
        return False
    except Exception as e:
        print(f"❌ Error loading order data: {e}")
        return False

    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return False

    try:
        with db_cursor(conn) as cursor:

            # Step 1: Delete Payment
            if 'payment_id' in order_data:
                print(
                    f"💳 Step 1: Deleting Payment (ID: {order_data['payment_id']})...")
                cursor.execute(
                    "DELETE FROM payments WHERE payment_id = %s", (order_data['payment_id'],))
                if cursor.rowcount > 0:
                    print("✅ Payment deleted")
                else:
                    print("⚠️  Payment not found (may have been deleted already)")

            # Step 2: Delete Order Items
            if 'order_items' in order_data:
                print(f"\n🧼 Step 2: Deleting Order Items...")
                for item in order_data['order_items']:
                    cursor.execute(
                        "DELETE FROM order_items WHERE order_item_id = %s", (item['order_item_id'],))
                    if cursor.rowcount > 0:
                        print(
                            f"   ✅ Deleted order item: {item['service_name']}")
                    else:
                        print(
                            f"   ⚠️  Order item not found: {item['service_name']}")

            # Step 3: Delete Order
            if 'order_id' in order_data:
                print(
                    f"\n📋 Step 3: Deleting Order (ID: {order_data['order_id']})...")
                cursor.execute(
                    "DELETE FROM orders WHERE order_id = %s", (order_data['order_id'],))
                if cursor.rowcount > 0:
                    print("✅ Order deleted")
                else:
                    print("⚠️  Order not found (may have been deleted already)")

            # Step 4: Delete Customer
            if 'customer_id' in order_data:
                print(
                    f"\n👤 Step 4: Deleting Customer (ID: {order_data['customer_id']})...")
                cursor.execute(
                    "DELETE FROM customers WHERE customer_id = %s", (order_data['customer_id'],))
                if cursor.rowcount > 0:
                    print("✅ Customer deleted")
                else:
                    print("⚠️  Customer not found (may have been deleted already)")

            # Commit all deletions
            conn.commit()

            print(f"\n🎉 TEST ORDER DATA DELETED SUCCESSFULLY!")
            print(f"📊 Deletion Summary:")
            print(f"   ✅ Payment removed")
            print(f"   ✅ Order items removed")
            print(f"   ✅ Order removed")
            print(f"   ✅ Customer removed")

            # Clean up the JSON file
            try:
                os.remove('last_test_order.json')
                print(f"   ✅ Cleanup file removed")
            except:
                print(f"   ⚠️  Could not remove cleanup file")

            return True

    except Exception as e:
        print(f"❌ Error deleting order: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_by_ids():
    """
    Alternative method: Delete by manually entering IDs
    """
    print("🗑️  Manual Order Deletion\n")

    try:
        customer_id = input("Enter Customer ID to delete: ").strip()
        order_id = input("Enter Order ID to delete: ").strip()

        if not customer_id or not order_id:
            print("❌ Both Customer ID and Order ID are required!")
            return False

        customer_id = int(customer_id)
        order_id = int(order_id)

    except ValueError:
        print("❌ IDs must be numbers!")
        return False

    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return False

    try:
        with db_cursor(conn) as cursor:

            # Delete payments for this order
            cursor.execute(
                "DELETE FROM payments WHERE order_id = %s", (order_id,))
            payment_count = cursor.rowcount

            # Delete order items for this order
            cursor.execute(
                "DELETE FROM order_items WHERE order_id = %s", (order_id,))
            item_count = cursor.rowcount

            # Delete the order
            cursor.execute(
                "DELETE FROM orders WHERE order_id = %s", (order_id,))
            order_count = cursor.rowcount

            # Delete the customer
            cursor.execute(
                "DELETE FROM customers WHERE customer_id = %s", (customer_id,))
            customer_count = cursor.rowcount

            conn.commit()

            print(f"\n✅ Deletion completed:")
            print(f"   Payments deleted: {payment_count}")
            print(f"   Order items deleted: {item_count}")
            print(f"   Orders deleted: {order_count}")
            print(f"   Customers deleted: {customer_count}")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("Choose deletion method:")
    print("1. Delete last test order (automatic)")
    print("2. Delete by manual ID entry")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        delete_test_order()
    elif choice == "2":
        delete_by_ids()
    else:
        print("Invalid choice. Exiting.")
