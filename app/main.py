from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import api_router
from .core.config import settings
from .db.session import Base, engine
from app import models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Diagnostic Booking Service API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}