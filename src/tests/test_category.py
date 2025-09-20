from src.models.category import (
    add_category, get_category_by_id, get_all_categories, update_category, delete_category
)


def test_category_crud():
    # Create
    cat_id = add_category("Test Category")
    assert cat_id is not False

    # Read
    cat = get_category_by_id(cat_id)
    assert cat is not None
    assert cat["category_name"] == "Test Category"

    # Update
    assert update_category(cat_id, "Updated Category")
    updated = get_category_by_id(cat_id)
    assert updated["category_name"] == "Updated Category"

    # List
    all_cats = get_all_categories()
    assert any(c["category_id"] == cat_id for c in all_cats)

    # Delete
    assert delete_category(cat_id)
    assert get_category_by_id(cat_id) is None


if __name__ == "__main__":
    test_category_crud()
    print("Category model tests passed.")
