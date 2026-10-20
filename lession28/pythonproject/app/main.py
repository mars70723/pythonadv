from fastapi import FastAPI,HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from trying import Optional
from dotenv import load_dotenv
import os
from app.database import get_db, init_db

load_dotenv()
app=FastAPI()
init_db()

api_key_header = APIKeyHeader(name="api-key")

def check_key(key:str = Depends(api_key_header)):
    allowed_keys = os.getenv("API_KEYS", "").split(",")
    if not key or key not in allowed_keys:
        raise HTTPException(401,"Invalid API Key")

class Item(BaseModel):
    name:str
    description:Optional[str]=None

@app.post("/items", dependencies=[Depends(check_key())])
def create_item(item:Item):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO items(names, description) VALUES(?,?)"
            (item.name,item.description)
        )
        return {"id":cursor.lastrowid, **item.model_dump()}

@app.get("/items/", dependencies=[Depends(check_key())])
def get_item():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM items").fetchall()
        return [dict(row) for row in rows]

@app.get("/items/{item_id}", dependencies=[Depends(check_key())])
def get_item(item_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Item not found")
        return [dict(row)]

@app.put("/items/{item_id}", dependencies=[Depends(check_key())])
def update_item(item_id: int, item: Item):
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE items SET name=?, description=? WHERE id=?",
            (item.name, item.description, item_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(404, "Item not found")
        return {id: item_id, **item.model_dump()}
