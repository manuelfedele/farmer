import datetime
import json

from fastapi import FastAPI
import uvicorn

app = FastAPI()
data = json.load(open("data/bars.json"))


@app.get("/")
def bars():
    return data


if __name__ == "__main__":

    uvicorn.run("backend:app")
