from fastapi import FastAPI
from app.database import engine
from app import models
from .database import engine
from .models import Base

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "MicroMatch API running"}


Base.metadata.create_all(bind=engine)
