from models.order_status import get_all_order_statuses
from models.category import get_all_categories
from models.service import get_all_services
from models.customer import get_all_customers, add_customer
import sys
import os
# Add the project root to Python path
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


def test_models():
    print("🧪 Testing Database Models...\n")

    # Test Categories
    print("📂 Testing Categories:")
    categories = get_all_categories()
    if categories:
        print(f"✅ Found {len(categories)} categories:")
        for cat in categories:
            print(f"   - {cat['category_name']} (ID: {cat['category_id']})")
    else:
        print("❌ No categories found")
    print()

    # Test Services
    print("🧼 Testing Services:")
    services = get_all_services()
    if services:
        print(f"✅ Found {len(services)} services:")
        for service in services[:5]:  # Show first 5
            print(
                f"   - {service['service_name']}: ₱{service['min_price']}-₱{service['max_price']} {service['price_unit']}")
        if len(services) > 5:
            print(f"   ... and {len(services) - 5} more services")
    else:
        print("❌ No services found")
    print()

    # Test Order Statuses
    print("📋 Testing Order Statuses:")
    statuses = get_all_order_statuses()
    if statuses:
        print(f"✅ Found {len(statuses)} order statuses:")
        for status in statuses:
            print(
                f"   - {status['order_status_name']} (ID: {status['order_status_id']})")
    else:
        print("❌ No order statuses found")
    print()

    # Test Customers
    print("👥 Testing Customers:")
    customers = get_all_customers()
    print(f"✅ Found {len(customers)} customers in database")

    # Test adding a customer (optional)
    print("\n🆕 Testing Add Customer:")
    try:
        customer_id = add_customer(
            name="Test Customer",
            phone="09123456789",
            email="test@example.com",
            address="123 Test Street"
        )
        if customer_id:
            print(f"✅ Successfully added test customer with ID: {customer_id}")

            # Clean up - delete the test customer
            from src.models.customer import delete_customer
            if delete_customer(customer_id):
                print("✅ Test customer cleaned up successfully")
        else:
            print("❌ Failed to add test customer")
    except Exception as e:
        print(f"❌ Error testing add customer: {e}")

    print("\n🎉 Model testing completed!")


if __name__ == "__main__":
    test_models()
