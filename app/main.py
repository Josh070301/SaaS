from fastapi import FastAPI
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
                "/images/upload/"
            },
            "documents": {
                "/documents/summarize/"
            }
        }
    }