from src.models.order import (
    add_order, get_order_by_id, get_all_orders, update_order, delete_order
)
from src.models.customer import add_customer, delete_customer
from src.models.order_status import add_order_status, delete_order_status
import datetime


def test_order_crud():
    cust_id = add_customer("OrderTest Cust", "0900", "o@x.com", "Addr")
    os_id = add_order_status("OrderTest Status")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create
    order_id = add_order(cust_id, os_id, now, 111.50)
    assert order_id is not False

    # Read
    order = get_order_by_id(order_id)
    assert order and order["customer_id"] == cust_id

    # Update
    assert update_order(order_id, cust_id, os_id, now, 200.75)
    upd = get_order_by_id(order_id)
    assert upd["total_price"] == 200.75

    # List
    all_orders = get_all_orders()
    assert any(o["order_id"] == order_id for o in all_orders)

    # Delete
    assert delete_order(order_id)
    assert get_order_by_id(order_id) is None

    delete_customer(cust_id)
    delete_order_status(os_id)


if __name__ == "__main__":
    test_order_crud()
    print("Order model tests passed.")
