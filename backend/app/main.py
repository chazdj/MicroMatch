from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from app.routers import auth
from app.routers import student_profile
from app.routers import organization_profile
from app.routers import projects
from app.routers import applications
from app.routers import deliverables
from app.routers import feedback
from app.routers import admin
from app.routers import notifications
from app.routers import recommendations
from app.routers import messages
from app.routers import analytics
from .middleware.logging_middleware import LoggingMiddleware

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

app.add_middleware(LoggingMiddleware)

# Register routers
app.include_router(auth.router)
app.include_router(student_profile.router)
app.include_router(organization_profile.router)
app.include_router(projects.router)
app.include_router(applications.router)
app.include_router(deliverables.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(notifications.router)
app.include_router(recommendations.router)
app.include_router(messages.router)
app.include_router(analytics.router)

# Create tables
Base.metadata.create_all(bind=engine)