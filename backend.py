import json

import uvicorn
from fastapi import FastAPI

app = FastAPI()
data = json.load(open("data/bars.json"))


@app.get("/")
def bars(exchange: str = None):
    if exchange is None:
        return data
    else:
        new_data = []
        for element in data:
            if element['exchange'] == exchange:
                new_data.append(element)
        return new_data


if __name__ == "__main__":

    uvicorn.run("backend:app")
