from src.models.payment_status import (
    add_payment_status, get_payment_status_by_id, get_all_payment_statuses,
    update_payment_status, delete_payment_status
)


def test_payment_status_crud():
    # Create
    ps_id = add_payment_status("TestPayStatus")
    assert ps_id is not False

    # Read
    ps = get_payment_status_by_id(ps_id)
    assert ps and ps["payment_status_name"] == "TestPayStatus"

    # Update
    assert update_payment_status(ps_id, "UpdatedPayStatus")
    upd = get_payment_status_by_id(ps_id)
    assert upd["payment_status_name"] == "UpdatedPayStatus"

    # List
    all_ps = get_all_payment_statuses()
    assert any(p["payment_status_id"] == ps_id for p in all_ps)

    # Delete
    assert delete_payment_status(ps_id)
    assert get_payment_status_by_id(ps_id) is None


if __name__ == "__main__":
    test_payment_status_crud()
    print("Payment status model tests passed.")
