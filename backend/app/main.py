from fastapi import FastAPI
from app.database import engine
from app import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "MicroMatch API running"}
