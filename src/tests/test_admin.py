from src.models.admin import (
    add_admin, get_admin_by_id, get_admin_by_username, update_admin, delete_admin
)
import datetime


def test_admin_crud():
    # Create
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    admin_id = add_admin("testadmin", "test@x.com",
                         "password123", created_at, "Test Admin")
    assert admin_id is not False

    # Read by id
    admin = get_admin_by_id(admin_id)
    assert admin and admin["username"] == "testadmin"

    # Read by username
    admin2 = get_admin_by_username("testadmin")
    assert admin2 and admin2["admin_id"] == admin_id

    # Update
    assert update_admin(admin_id, "updadmin", "u@x.com", "newpass", "Upd Name")
    upd = get_admin_by_id(admin_id)
    assert upd["username"] == "updadmin"

    # Delete
    assert delete_admin(admin_id)
    assert get_admin_by_id(admin_id) is None


if __name__ == "__main__":
    test_admin_crud()
    print("Admin model tests passed.")
