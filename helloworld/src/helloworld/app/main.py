import uvicorn
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from helloworld.app.func import add,sub

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    print("3 + 2 =",add(3,2))
    print("3 - 2 =",sub(3,2))
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

def main():
    # Your app logic goes here
    uvicorn.run(app=app, host="127.0.0.1", port=9500)


