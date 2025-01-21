import json
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import aiohttp
import asyncio
import json

app = FastAPI()

API_URL = "https://jsonplaceholder.typicode.com/posts"

class PostData(BaseModel):
    title: str
    body: str
    userId: int

# Asynchronous function to make GET or POST requests and handle errors
async def fetch_data(url: str, method: str, json_data: dict = None):
    """
    Makes an asynchronous GET or POST request to the given URL and returns the response data.
    Handles errors including client response errors and timeouts.
    """
    try:
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method == 'POST':
                async with session.post(url, json=json_data) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Method not allowed")
    except aiohttp.ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=f"Request failed: {e.message}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Fetch the first 5 posts from the external API
@app.get("/get_posts")
async def get_posts():
    """
    Fetches and returns the first 5 posts from the external API.
    """
    posts = await fetch_data(API_URL, 'GET')
    return {"status": "success", "posts": posts[:5]}


# Create a new post and return the created post's details
@app.post("/create_post")
async def create_post(post_data: PostData):
    """
    Creates a new post by sending data to the external API and returns the created post's details.
    """
    created_post = await fetch_data(API_URL, 'POST', post_data.dict())
    print("Created Post:", json.dumps(created_post, indent=4))
    return {"status": "success", "created_post": created_post}


# A simple test route to check server functionality
@app.get("/")
async def test_async():
    """
    A test route that verifies if the server is running successfully.
    """
    return {"message": "task completed successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
