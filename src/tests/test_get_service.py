# test_db_simple.py
from models.service import get_all_services
print("Testing database...")

print("Calling get_all_services()...")
services = get_all_services()
print(f"Got {len(services)} services")
for s in services[:18]:
    print(f"  - {s['service_name']}")
print("Done!")
