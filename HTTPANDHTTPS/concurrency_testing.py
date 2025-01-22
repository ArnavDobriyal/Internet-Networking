import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000/api"

def create_item(name, description):
    """Send a POST request to create an item."""
    response = requests.post(f"{BASE_URL}/items/", json={"name": name, "description": description})
    return {"task": "create", "name": name, "status": response.status_code, "response": response.json()}

def delete_item(name):
    """Send a DELETE request to delete an item."""
    response = requests.delete(f"{BASE_URL}/items/{name}")
    return {"task": "delete", "name": name, "status": response.status_code, "response": response.json()}

def get_data():
    """Send a GET request to fetch all items."""
    response = requests.get(f"{BASE_URL}/data")
    return {"task": "fetch", "status": response.status_code, "response": response.json()}

def test_concurrent_tasks():
    """Test multiple concurrent tasks on the API."""
    print("Starting concurrent task tests...\n")

    tasks = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create multiple items concurrently
        for i in range(5):
            tasks.append(executor.submit(create_item, f"item{i}", f"Description for item{i}"))

        # Delete items concurrently
        for i in range(3):
            tasks.append(executor.submit(delete_item, f"item{i}"))

        # Fetch data concurrently
        for _ in range(5):
            tasks.append(executor.submit(get_data))

        # Wait for all tasks to complete
        for future in as_completed(tasks):
            result = future.result()
            print(f"Task: {result['task']}, Name: {result.get('name', 'N/A')}, Status: {result['status']}, Response: {result['response']}")

    print("\nConcurrent task tests completed.")

if __name__ == "__main__":
    print("Testing API with multiple concurrent tasks...\n")
    test_concurrent_tasks()
