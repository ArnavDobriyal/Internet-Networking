from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

    # Private variable
    _name: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set the private attribute _name
        self._name = self.name

    def print_name(self):
        """
        Prints the private _name variable.
        """
        print(f"The private name is: {self._name}")

    def public_dict(self):
        """
        Returns only the safe public attributes of the Item object.
        """
        return {"name": self.name, "description": self.description}


stored_items: List[Item] = []

@app.get("/")
async def read_root():
    """
    Simple root endpoint to check if the server is running.
    """
    return {"message": "Welcome to the HTTP Server!"}

@app.get("/api/data")
async def get_data():
    """
    Fetch all stored items with only public fields.
    """
    return {"stored_items": [item.public_dict() for item in stored_items]}

@app.post("/api/items/")
async def create_item(item: Item):
    """
    Add a new item to the stored_items list and print the private name.
    """
    stored_items.append(item)
    item.print_name()  # Call the print_name function to display the private name
    return {"message": "Item added successfully."}  # No need to return the name or description here

@app.delete("/api/items/{item_name}")
async def delete_item(item_name: str):
    """
    Delete an item by its name.
    """
    global stored_items
    stored_items = [item for item in stored_items if item.name != item_name]
    return {"message": f"Item with name '{item_name}' deleted successfully."}

def main():
    """
    Entry point for the application when run as a script.
    Runs the FastAPI server.
    """
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main()
