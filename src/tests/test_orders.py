# test_orders.py
from models.order import get_all_orders
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


try:
    orders = get_all_orders()
    print(f"Number of orders: {len(orders)}")
    if orders:
        print(f"First order type: {type(orders[0])}")
        print(f"First order: {orders[0]}")
    else:
        print("No orders found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
