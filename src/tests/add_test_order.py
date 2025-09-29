from db.connection import get_db_connection, db_cursor
import sys
import os
from datetime import datetime

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))


def add_student_order():
    """
    Test script to add a student customer's order with:
    1. Customer
    2. Order
    3. Order Items (basic laundry services)
    4. Payment
    """
    print("🛒 Creating Student Laundry Test Data...\n")

    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return None

    order_data = {}

    try:
        with db_cursor(conn) as cursor:

            # Step 1: Add Customer
            print("👤 Step 1: Adding Customer...")
            customer_sql = """
                INSERT INTO customers (customer_name, customer_phone, customer_email, customer_address)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(customer_sql, (
                "Juan Dela Cruz",
                "09175551234",
                "juan.delacruz@studentmail.com",
                "Dormitory A, University Belt, Manila"
            ))
            customer_id = cursor.lastrowid
            order_data['customer_id'] = customer_id
            print(f"✅ Customer added with ID: {customer_id}")

            # Step 2: Add Order
            print("\n📋 Step 2: Adding Order...")
            order_date = datetime.now()
            order_status_id = 1  # Pending Payment
            total_price = 0  # Will calculate later

            order_sql = """
                INSERT INTO orders (customer_id, order_status_id, order_date, total_price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                order_sql, (customer_id, order_status_id, order_date, total_price))
            order_id = cursor.lastrowid
            order_data['order_id'] = order_id
            print(f"✅ Order added with ID: {order_id}")

            # Step 3: Add Order Items (Services)
            print("\n🧼 Step 3: Adding Order Items...")

            # Student uses Machine Wash & Dry + Hand Wash & Dry
            service_ids = [1, 2]  # Machine Wash & Dry, Hand Wash & Dry
            cursor.execute(
                "SELECT service_id, service_name, min_price FROM services WHERE service_id IN (%s, %s)",
                service_ids
            )
            services = cursor.fetchall()

            order_items = []
            total_calculated = 0

            for i, service in enumerate(services):
                quantity = 5 if service['service_id'] == 1 else 2
                # 5 kg Machine Wash & Dry, 2 kg Hand Wash & Dry
                price = float(service['min_price']) * quantity
                total_calculated += price

                order_item_sql = """
                    INSERT INTO order_items (order_id, service_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(order_item_sql, (order_id,
                               service['service_id'], quantity, price))
                order_item_id = cursor.lastrowid

                order_items.append({
                    'order_item_id': order_item_id,
                    'service_id': service['service_id'],
                    'service_name': service['service_name'],
                    'quantity': quantity,
                    'price': price
                })

                print(
                    f"   ✅ Added {quantity}{'kg' if service['service_id'] in (1, 2) else ''} {service['service_name']} - ₱{price:.2f}")

            order_data['order_items'] = order_items
            order_data['total_price'] = total_calculated

            # Step 4: Update Order Total
            print(
                f"\n💰 Step 4: Updating Order Total to ₱{total_calculated:.2f}...")
            update_order_sql = "UPDATE orders SET total_price = %s WHERE order_id = %s"
            cursor.execute(update_order_sql, (total_calculated, order_id))
            print("✅ Order total updated")

            # Step 5: Add Payment
            print("\n💳 Step 5: Adding Payment...")
            payment_sql = """
                INSERT INTO payments (order_id, amount_paid, payment_date, payment_method_id, payment_status_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            payment_date = datetime.now()
            payment_method_id = 1  # Cash
            payment_status_id = 3  # Paid

            cursor.execute(payment_sql, (
                order_id,
                total_calculated,
                payment_date,
                payment_method_id,
                payment_status_id
            ))
            payment_id = cursor.lastrowid
            order_data['payment_id'] = payment_id
            print(f"✅ Payment added with ID: {payment_id}")

            # Step 6: Update Order Status to Queueing
            print("\n📋 Step 6: Updating Order Status to 'Queueing'...")
            cursor.execute(
                "UPDATE orders SET order_status_id = 2 WHERE order_id = %s", (order_id,))
            print("✅ Order status updated to 'Queueing'")

            # Commit all changes
            conn.commit()

            # Display Summary
            print(f"\n🎉 STUDENT ORDER CREATED SUCCESSFULLY!")
            print(f"📊 Order Summary:")
            print(f"   Customer ID: {customer_id} (Juan Dela Cruz)")
            print(f"   Order ID: {order_id}")
            print(f"   Order Items: {len(order_items)} services")
            print(f"   Total Amount: ₱{total_calculated:.2f}")
            print(f"   Payment ID: {payment_id}")
            print(f"   Status: Queueing (Paid)")

            # # Save order data to file for deletion script
            # import json
            # with open('last_student_order.json', 'w') as f:
            #     order_data_json = order_data.copy()
            #     json.dump(order_data_json, f, indent=2, default=str)

            # print(f"\n💾 Order details saved to 'last_student_order.json'")
            # print(f"🗑️  Use 'delete_test_order.py' to remove this test data")

            # return order_data

    except Exception as e:
        print(f"❌ Error creating order: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


if __name__ == "__main__":
    add_student_order()
