from src.models.order_item import (
    add_order_item, get_order_item_by_id, get_order_items_by_order, update_order_item, delete_order_item
)
from src.models.order import add_order, delete_order
from src.models.service import add_service, delete_service
from src.models.customer import add_customer, delete_customer
from src.models.order_status import add_order_status, delete_order_status
from src.models.category import add_category, delete_category
import datetime


def test_order_item_crud():
    cat_id = add_category("OrderItemCat")
    service_id = add_service(cat_id, "OrderItemService", 1, 2, "kg", "oi note")
    cust_id = add_customer("OI Cust", "0900", "oi@x.com", "Addr")
    os_id = add_order_status("OI Status")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_id = add_order(cust_id, os_id, now, 100)

    # Create
    oi_id = add_order_item(order_id, service_id, 5, 50.0)
    assert oi_id is not False

    # Read by id
    oi = get_order_item_by_id(oi_id)
    assert oi and oi["order_id"] == order_id

    # Read by order
    items = get_order_items_by_order(order_id)
    assert any(i["order_item_id"] == oi_id for i in items)

    # Update
    assert update_order_item(oi_id, order_id, service_id, 10, 88.0)
    upd = get_order_item_by_id(oi_id)
    assert upd["quantity"] == 10

    # Delete
    assert delete_order_item(oi_id)
    assert get_order_item_by_id(oi_id) is None

    delete_order(order_id)
    delete_service(service_id)
    delete_category(cat_id)
    delete_customer(cust_id)
    delete_order_status(os_id)


if __name__ == "__main__":
    test_order_item_crud()
    print("Order item model tests passed.")
