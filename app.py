import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi.responses import JSONResponse

load_dotenv()
# Initialize FastAPI app
app = FastAPI()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL") # Replace with your Supabase URL
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Replace with your Supabase API key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the Item model without time_date
class Item(BaseModel):
    task_name: str
    task_description: Optional[str] = None

# Create item
@app.post("/create_log", response_model=Item)
def create_item(item: Item): # Generate a unique ID for each item
    data = {
        "task_name": item.task_name,
        "task_description": item.task_description,
    }
    response = supabase.table("company_logs").insert(data).execute()
    print(response)
    if response:
        return item
    raise HTTPException(status_code=500, detail="Failed to create item")

# Read all items
@app.get("/read_logs")
def read_all_items():
    response = supabase.table("company_logs").select("*").execute()
    if response:
        return response.data
    raise HTTPException(status_code=500, detail="Failed to create item")


@app.get("/get_logs_by_id", response_model=Item)
def get_item_by_id(item_id: str):
    response = supabase.table("company_logs").select("*").eq("id", item_id).execute()

    # Check if an item was found
    if response.data:
        item_data = response.data[0]
        return Item(**item_data)

    raise HTTPException(status_code=404, detail="Item not found")

# Delete item
@app.delete("/delete_log", response_model=dict)
def delete_item(item_id: str):
    response = supabase.table("company_logs").delete().eq("id", item_id).execute()
    if response:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete item")

# Modify item
@app.put("/modify_log", response_model=Item)
def modify_item(item_id: str, item: Item):
    data = {
        "task_name": item.task_name,
        "task_description": item.task_description,
    }
    response = supabase.table("company_logs").update(data).eq("id", item_id).execute()
    if response:
        updated_item = response.data[0]
        return Item(**updated_item)
    raise HTTPException(status_code=500, detail="Failed to update item")