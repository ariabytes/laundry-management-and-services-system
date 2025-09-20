from src.models.service import (
    add_service, get_service_by_id, get_all_services, update_service, delete_service
)
from src.models.category import add_category, delete_category


def test_service_crud():
    cat_id = add_category("ServiceCat")
    # Create
    s_id = add_service(cat_id, "Test Service", 10, 20, "kg", "test notes")
    assert s_id is not False

    # Read
    s = get_service_by_id(s_id)
    print("Service fetched:", s)  # Diagnostic
    assert s is not None
    assert s["service_name"] == "Test Service"
    assert s["service_notes"] == "test notes"

    # Update
    assert update_service(s_id, cat_id, "Updated Service",
                          15, 25, "load", "updated notes")
    updated = get_service_by_id(s_id)
    assert updated["service_name"] == "Updated Service"
    assert updated["service_notes"] == "updated notes"

    # List
    all_s = get_all_services()
    assert any(item["service_id"] == s_id for item in all_s)

    # Delete
    assert delete_service(s_id)
    assert get_service_by_id(s_id) is None
    delete_category(cat_id)


if __name__ == "__main__":
    test_service_crud()
    print("Service model tests passed.")
