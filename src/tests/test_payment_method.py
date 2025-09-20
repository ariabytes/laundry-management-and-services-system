from src.models.payment_method import (
    add_payment_method, get_payment_method_by_id, get_all_payment_methods,
    update_payment_method, delete_payment_method
)


def test_payment_method_crud():
    # Create
    pm_id = add_payment_method("TestMethod")
    assert pm_id is not False

    # Read
    pm = get_payment_method_by_id(pm_id)
    assert pm and pm["payment_method_name"] == "TestMethod"

    # Update
    assert update_payment_method(pm_id, "UpdatedMethod")
    upd = get_payment_method_by_id(pm_id)
    assert upd["payment_method_name"] == "UpdatedMethod"

    # List
    all_pm = get_all_payment_methods()
    assert any(m["payment_method_id"] == pm_id for m in all_pm)

    # Delete
    assert delete_payment_method(pm_id)
    assert get_payment_method_by_id(pm_id) is None


if __name__ == "__main__":
    test_payment_method_crud()
    print("Payment method model tests passed.")
