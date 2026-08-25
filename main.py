from fastapi import FastAPI
from database import getdb

app=FastAPI()

@app.get("/health")
def check_health():


    return{
        "status":"running"
    }
