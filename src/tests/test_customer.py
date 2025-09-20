from src.models.customer import (
    add_customer, get_customer_by_id, get_all_customers, update_customer, delete_customer
)


def test_customer_crud():
    # Create
    cust_id = add_customer("Test User", "099999999", "test@x.com", "Somewhere")
    assert cust_id is not False

    # Read
    cust = get_customer_by_id(cust_id)
    assert cust and cust["customer_name"] == "Test User"

    # Update
    assert update_customer(cust_id, "Updated User",
                           "088888888", "upd@x.com", "Somewhere Else")
    upd = get_customer_by_id(cust_id)
    assert upd["customer_name"] == "Updated User"

    # List
    all_c = get_all_customers()
    assert any(c["customer_id"] == cust_id for c in all_c)

    # Delete
    assert delete_customer(cust_id)
    assert get_customer_by_id(cust_id) is None


if __name__ == "__main__":
    test_customer_crud()
    print("Customer model tests passed.")
