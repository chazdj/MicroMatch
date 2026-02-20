from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from app.routers import auth
from app.routers import student_profile
from app.routers import organization_profile
from app.routers import projects

app = FastAPI()

# Allow CORS for frontend
origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow only your frontend
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

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