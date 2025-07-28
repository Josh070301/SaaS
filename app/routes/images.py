from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path

# Get the service URL from environment variables with a default value
SERVICE_URL = os.getenv("SERVICE_URL", "http://localhost:8000")

router = APIRouter(prefix="/images", tags=["images"])

# Base directory for uploads
UPLOAD_DIR = "uploads"

# Define allowed image extensions
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", 
    ".webp", ".tiff", ".tif", ".svg", ".heic"
}

def is_valid_image(filename: str) -> bool:
    """
    Check if the file has a valid image extension.
    """
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_EXTENSIONS

@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    folder: Optional[str] = Query(None, description="Subfolder to save the image(s)")
):
    """
    Upload multiple image files simultaneously.
    Optionally specify a subfolder to save the images.
    Only accepts valid image file extensions.
    Returns a list of successfully uploaded filenames with their access URLs.
    """
    # Determine the target directory
    target_dir = UPLOAD_DIR
    if folder:
        # Create path safely and avoid directory traversal attacks
        target_dir = os.path.join(UPLOAD_DIR, folder)
        os.makedirs(target_dir, exist_ok=True)
    
    uploaded_files = []
    for file in files:
        if not is_valid_image(file.filename):
            uploaded_files.append({
                "filename": file.filename,
                "status": "failed",
                "error": "Invalid file type. Only image files are allowed."
            })
            continue
            
        try:
            file_path = os.path.join(target_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create the URL path where the image can be accessed
            access_path = f"{SERVICE_URL}/images/get/{folder + '/' if folder else ''}{file.filename}"
            
            uploaded_files.append({
                "filename": file.filename,
                "status": "success",
                "url": access_path
            })
        except Exception as e:
            uploaded_files.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {"uploaded_files": uploaded_files}

@router.get("/list/{folder_path:path}")
async def list_images(folder_path: Optional[str] = ""):
    """
    List all images in the specified folder or root uploads folder.
    """
    try:
        target_dir = os.path.join(UPLOAD_DIR, folder_path)
        # Ensure path is valid and doesn't allow traversal attacks
        target_dir = os.path.normpath(target_dir)
        if not target_dir.startswith(UPLOAD_DIR):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        
        if not os.path.exists(target_dir):
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
        
        files = os.listdir(target_dir)
        image_files = []
        
        for file in files:
            if os.path.isfile(os.path.join(target_dir, file)) and is_valid_image(file):
                # Create the URL path where the image can be accessed
                access_path = f"{SERVICE_URL}/images/get/{folder_path + '/' if folder_path else ''}{file}"
                image_files.append({
                    "filename": file,
                    "url": access_path
                })
        
        return {"images": image_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@router.get("/get/{file_path:path}")
async def get_image(file_path: str):
    """
    Retrieve a specific image file.
    """
    try:
        # Build the file path
        image_path = os.path.join(UPLOAD_DIR, file_path)
        
        # Ensure path is valid and doesn't allow traversal attacks
        image_path = os.path.normpath(image_path)
        if not image_path.startswith(UPLOAD_DIR):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        if not os.path.isfile(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Verify file is actually an image
        if not is_valid_image(image_path):
            raise HTTPException(status_code=400, detail="Requested file is not a valid image")
            
        return FileResponse(image_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")