from fastapi import FastAPI
from .database import engine
from .models import Base
from app.routers import auth

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "MicroMatch API running"}