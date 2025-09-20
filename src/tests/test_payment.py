from src.models.payment import (
    add_payment, get_payment_by_id, get_payments_by_order, update_payment, delete_payment
)
from src.models.order import add_order, delete_order
from src.models.customer import add_customer, delete_customer
from src.models.order_status import add_order_status, delete_order_status
from src.models.payment_status import add_payment_status, delete_payment_status
from src.models.payment_method import add_payment_method, delete_payment_method
import datetime


def test_payment_crud():
    # Setup dependencies
    cust_id = add_customer("Pay Cust", "0911", "pay@x.com", "Addr")
    os_id = add_order_status("Pay Status")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_id = add_order(cust_id, os_id, now, 999.0)
    ps_id = add_payment_status("PayStat")
    pm_id = add_payment_method("PayMeth")

    # Create
    pay_date = now
    pay_id = add_payment(order_id, 500.0, pay_date, ps_id, pm_id)
    assert pay_id is not False

    # Read by id
    pay = get_payment_by_id(pay_id)
    assert pay and pay["order_id"] == order_id

    # Read by order
    pays = get_payments_by_order(order_id)
    assert any(p["payment_id"] == pay_id for p in pays)

    # Update
    assert update_payment(pay_id, order_id, 700.0, pay_date, ps_id, pm_id)
    upd = get_payment_by_id(pay_id)
    assert upd["amount_paid"] == 700.0

    # Delete
    assert delete_payment(pay_id)
    assert get_payment_by_id(pay_id) is None

    # Teardown
    delete_payment_status(ps_id)
    delete_payment_method(pm_id)
    delete_order(order_id)
    delete_customer(cust_id)
    delete_order_status(os_id)


if __name__ == "__main__":
    test_payment_crud()
    print("Payment model tests passed.")
