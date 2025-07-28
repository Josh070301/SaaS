from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Import routers
from app.routes import documents, images

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="SaaS API",
    description="A SaaS API for file uploads and text summarization",
    version="0.1.0"
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Include routers from route modules
app.include_router(documents.router)
app.include_router(images.router)

# Mount the uploads directory as a static files directory
# This is an alternative way to serve files directly
app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "message": "Welcome to the SaaS API",
        "docs": "/docs",
        "endpoints": {
            "images": {
                "/images/upload/": "Upload images (POST)",
                "/images/get/{file_path}": "Get specific image (GET)",
                "/images/list/{folder_path}": "List images in folder (GET)"
            },
            "documents": {
                "/documents/summarize/": "Summarize text (POST)"
            }
        }
    }