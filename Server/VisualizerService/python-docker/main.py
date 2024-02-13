import asyncio
import time as time

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Your custom logic
shared_state = {"receivedData": 0, "data": []}


class Item(BaseModel):
    X: float
    Y: float


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(custom_logic())

@app.post("/visualizer")
async def visualizer(item: Item):
    print(item)
    shared_state["receivedData"] = 1
    shared_state["data"] = item.json
    print("Message received ")
    print(shared_state["data"])
    return {"message": "Notification received"}
body = []


async def custom_logic():
    while True:
        if(shared_state["receivedData"] == 1):
            print("Data has been received by the Visualizer.....")
            shared_state["receivedData"] = 0
        await asyncio.sleep(1)