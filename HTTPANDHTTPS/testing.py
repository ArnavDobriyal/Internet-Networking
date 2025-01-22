import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_get_data():
    """Test the GET /api/data endpoint."""
    response = requests.get(f"{BASE_URL}/data")
    print("GET /api/data:", response.status_code, response.json())

def test_create_item(name, description):
    """Test the POST /api/items/ endpoint."""
    data = {"name": name, "description": description}
    response = requests.post(f"{BASE_URL}/items/", json=data)
    print(f"POST /api/items/ with name='{name}', description='{description}':", response.status_code, response.json())

def test_delete_item(name):
    """Test the DELETE /api/items/{item_name} endpoint."""
    response = requests.delete(f"{BASE_URL}/items/{name}")
    print(f"DELETE /api/items/{name}:", response.status_code, response.json())

def test_edge_cases():
    """Run edge case tests."""
    # 1. Normal case
    test_create_item("item1", "This is item1")

    # 2. Duplicate name
    test_create_item("item1", "Duplicate item1 description")

    # 3. Missing description
    test_create_item("item2", None)

    # 4. Empty name
    test_create_item("", "Empty name")

    # 5. Name too long
    long_name = "a" * 1001
    test_create_item(long_name, "Name too long")

    # 6. Special characters in name
    special_name = "!@#$%^&*()_+{}|:\"<>?"
    test_create_item(special_name, "Special characters in name")

    # 7. Invalid data type for name
    try:
        response = requests.post(f"{BASE_URL}/items/", json={"name": 123, "description": "Invalid name type"})
        print("POST /api/items/ with invalid name type:", response.status_code, response.json())
    except Exception as e:
        print("POST /api/items/ with invalid name type raised exception:", str(e))

    # 8. Missing name field
    try:
        response = requests.post(f"{BASE_URL}/items/", json={"description": "Missing name field"})
        print("POST /api/items/ with missing name field:", response.status_code, response.json())
    except Exception as e:
        print("POST /api/items/ with missing name field raised exception:", str(e))

    # 9. Deleting non-existent item
    test_delete_item("non_existent_item")

    # 10. Mixed case sensitivity
    test_create_item("ITEM1", "Uppercase name")
    test_delete_item("item1")  
    test_get_data()  

if __name__ == "__main__":
    print("Running edge case tests...\n")
    test_get_data()  
    test_edge_cases()
    print("\nTests completed.")
