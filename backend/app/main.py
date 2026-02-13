from fastapi import FastAPI
from .database import engine
from .models import Base
from .database import SessionLocal
from .models import User

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "MicroMatch API running"}