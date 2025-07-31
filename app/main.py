from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routers
from app.routes import documents, images, csv

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="SaaS API",
    description="A SaaS API for file conversion and text summarization. This API was created by Joshua Laude so people can try and practice api integration",
    version="0.1.0"
)

# Get environment variables for CORS
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Setup CORS middleware with environment-specific settings
if ENVIRONMENT.lower() == "production":
    # Production: Use specific origins from .env
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
else:
    # Development: Allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Include routers from route modules
app.include_router(documents.router)
app.include_router(images.router)
app.include_router(csv.router)

# Mount the uploads directory as a static files directory
# This is an alternative way to serve files directly
app.mount("/static", StaticFiles(directory="uploads"), name="static")