from src.models.order_status import (
    add_order_status, get_order_status_by_id, get_all_order_statuses,
    update_order_status, delete_order_status
)


def test_order_status_crud():
    # Create
    status_id = add_order_status("TestStatus")
    assert status_id is not False

    # Read
    status = get_order_status_by_id(status_id)
    assert status and status["order_status_name"] == "TestStatus"

    # Update
    assert update_order_status(status_id, "UpdatedStatus")
    upd = get_order_status_by_id(status_id)
    assert upd["order_status_name"] == "UpdatedStatus"

    # List
    all_statuses = get_all_order_statuses()
    assert any(s["order_status_id"] == status_id for s in all_statuses)

    # Delete
    assert delete_order_status(status_id)
    assert get_order_status_by_id(status_id) is None


if __name__ == "__main__":
    test_order_status_crud()
    print("Order status model tests passed.")
