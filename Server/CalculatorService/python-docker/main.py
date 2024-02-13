import asyncio
import string
import time as time
import json

import uvicorn
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Your custom logic
shared_state = {"receivedData": 0, "data": {}}

class TagData(BaseModel):
    TAG_ID: str
    ANC1: float
    ANC2: float
    ANC3: float

A1 = {"x":0, "y":0}
A2 = {"x":1.6, "y":0}
A3 = {"x":0.8, "y":1.6}

def CalculateDistance(r1:float, r2:float, r3:float):
    A = 2 * A2["x"] - 2 * A1["x"]
    B = 2 * A2["y"] - 2 * A1["y"]
    C = r1 ** 2 - r2 ** 2 - A1["x"] ** 2 + A2["x"] ** 2 - A1["y"] ** 2 + A2["y"] ** 2
    D = 2 * A3["x"] - 2 * A2["x"]
    E = 2 * A3["y"] - 2 * A2["y"]
    F = r2 ** 2 - r3 ** 2 - A2["x"] ** 2 + A3["x"] ** 2 - A2["y"] ** 2 + A3["y"] ** 2

    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)

    print("X = ", round(x, 2))
    print("Y = ", round(y, 2))

    return round(x, 2), round(y, 2)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(custom_logic())

@app.post("/calculator")
async def CalculatorEndpoint(tag: TagData):
    print(tag)

    shared_state["receivedData"] = 1
    shared_state["data"] = tag.dict()
    print("Message received ")
    print(shared_state["data"])
    return {"message": "Notification received"}


async def custom_logic():
    while True:
        if(shared_state["receivedData"] == 1):
            print("Data has been received from the Proccesor ...")
            anchors = shared_state["data"]
            print("TEEEEEEEST ---- ", anchors)
            value = CalculateDistance(anchors["ANC1"], anchors["ANC2"], anchors["ANC3"])
            test = json.dumps({"X":value[0], "Y":value[1]})
            print(test)
            res = requests.post('http://192.168.153.237:8001/visualizer',
                                headers={
                                    'Content-type': 'application/json'
                                },
                                json={"X": value[0], "Y": value[1]}
                                )

            shared_state["receivedData"] = 0
        await asyncio.sleep(1)