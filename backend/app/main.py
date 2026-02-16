from fastapi import FastAPI
from .database import engine
from .models import Base
from app.routers import auth
from app.routers import student_profile
from app.routers import organization_profile
from app.routers import projects

app = FastAPI()

# Register routers
app.include_router(auth.router)
app.include_router(student_profile.router)
app.include_router(organization_profile.router)
app.include_router(projects.router)

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "MicroMatch API running"}