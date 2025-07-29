from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Response, Form
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path
import io
from PIL import Image

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

# @router.post("/upload")
# async def upload_files(
#     files: List[UploadFile] = File(...),
#     folder: Optional[str] = Query(None, description="Subfolder to save the image(s)")
# ):
#     """
#     Upload multiple image files simultaneously.
#     Optionally specify a subfolder to save the images.
#     Only accepts valid image file extensions.
#     Returns a list of successfully uploaded filenames with their access URLs.
#     ".jpg", ".jpeg", ".png", ".gif", ".bmp", 
#     ".webp", ".tiff", ".tif", ".svg", ".heic"
#     """
#     # Determine the target directory
#     target_dir = UPLOAD_DIR
#     if folder:
#         # Create path safely and avoid directory traversal attacks
#         target_dir = os.path.join(UPLOAD_DIR, folder)
#         os.makedirs(target_dir, exist_ok=True)
    
#     uploaded_files = []
#     for file in files:
#         if not is_valid_image(file.filename):
#             uploaded_files.append({
#                 "filename": file.filename,
#                 "status": "failed",
#                 "error": "Invalid file type. Only image files are allowed."
#             })
#             continue
            
#         try:
#             file_path = os.path.join(target_dir, file.filename)
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
            
#             # Create the URL path where the image can be accessed
#             access_path = f"{SERVICE_URL}/images/get/{folder + '/' if folder else ''}{file.filename}"
            
#             uploaded_files.append({
#                 "filename": file.filename,
#                 "status": "success",
#                 "url": access_path
#             })
#         except Exception as e:
#             uploaded_files.append({
#                 "filename": file.filename,
#                 "status": "failed",
#                 "error": str(e)
#             })
    
#     return {"uploaded_files": uploaded_files}

# @router.get("/list/{folder_path:path}")
# async def list_images(folder_path: Optional[str] = ""):
#     """
#     List all images in the specified folder or root uploads folder.
#     """
#     try:
#         target_dir = os.path.join(UPLOAD_DIR, folder_path)
#         # Ensure path is valid and doesn't allow traversal attacks
#         target_dir = os.path.normpath(target_dir)
#         if not target_dir.startswith(UPLOAD_DIR):
#             raise HTTPException(status_code=400, detail="Invalid folder path")
        
#         if not os.path.exists(target_dir):
#             raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
        
#         files = os.listdir(target_dir)
#         image_files = []
        
#         for file in files:
#             if os.path.isfile(os.path.join(target_dir, file)) and is_valid_image(file):
#                 # Create the URL path where the image can be accessed
#                 access_path = f"{SERVICE_URL}/images/get/{folder_path + '/' if folder_path else ''}{file}"
#                 image_files.append({
#                     "filename": file,
#                     "url": access_path
#                 })
        
#         return {"images": image_files}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

# @router.get("/get/{file_path:path}")
# async def get_image(file_path: str):
#     """
#     Retrieve a specific image file.
#     """
#     try:
#         # Build the file path
#         image_path = os.path.join(UPLOAD_DIR, file_path)
        
#         # Ensure path is valid and doesn't allow traversal attacks
#         image_path = os.path.normpath(image_path)
#         if not image_path.startswith(UPLOAD_DIR):
#             raise HTTPException(status_code=400, detail="Invalid file path")
        
#         if not os.path.isfile(image_path):
#             raise HTTPException(status_code=404, detail="Image not found")
        
#         # Verify file is actually an image
#         if not is_valid_image(image_path):
#             raise HTTPException(status_code=400, detail="Requested file is not a valid image")
            
#         return FileResponse(image_path)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")
    
@router.post("/convert-format")
async def convert_image_format(
    images: List[UploadFile] = File(...),
    target_format: str = Form(..., description="Target format (webp, jpg, png, etc.)"),
    quality: int = Form(85, description="Output quality (1-100, higher is better quality)")
):
    """
    Convert multiple uploaded images to a different format without saving to disk.
    Especially useful for optimizing images (e.g., PNG to WebP conversion).
    Returns a ZIP file containing all converted images.
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", 
    ".webp", ".tiff", ".tif", ".svg", ".heic"
    """
    import zipfile
    from datetime import datetime
    
    # Normalize target format (remove dot if present and convert to lowercase)
    target_format = target_format.lower().strip('.')
    
    # Check if target format is supported
    if f".{target_format}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported target format. Supported formats: {', '.join(ext.strip('.') for ext in ALLOWED_EXTENSIONS)}"
        )
    
    # Create a BytesIO object to store the ZIP file
    zip_buffer = io.BytesIO()
    
    # Create ZIP file
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add a metadata file with conversion info
        metadata = []
        
        # Process each image
        for image in images:
            # Validate input file is an image
            if not is_valid_image(image.filename):
                metadata.append({
                    "filename": image.filename,
                    "status": "failed",
                    "error": "Invalid file type. Only image files are allowed."
                })
                continue
                
            try:
                # Read the input image
                image_data = await image.read()
                input_image = Image.open(io.BytesIO(image_data))
                
                # Convert to RGB if saving as JPG (JPG doesn't support transparency)
                if target_format.lower() in ['jpg', 'jpeg'] and input_image.mode == 'RGBA':
                    input_image = input_image.convert('RGB')
                    
                # Create a BytesIO object to store the output image
                output_buffer = io.BytesIO()
                
                # Save with appropriate settings
                if target_format.lower() == 'webp':
                    input_image.save(output_buffer, format=target_format.upper(), quality=quality, method=6)
                elif target_format.lower() in ['jpg', 'jpeg']:
                    input_image.save(output_buffer, format=target_format.upper(), quality=quality, optimize=True)
                elif target_format.lower() == 'png':
                    input_image.save(output_buffer, format=target_format.upper(), optimize=True)
                else:
                    input_image.save(output_buffer, format=target_format.upper(), quality=quality)
                    
                # Get the size of both original and converted images
                input_size = len(image_data)
                output_buffer.seek(0)
                output_data = output_buffer.getvalue()
                output_size = len(output_data)
                
                # Generate a suitable filename for the converted image
                original_name = os.path.splitext(image.filename)[0]
                new_filename = f"{original_name}.{target_format}"
                
                # Add the converted image to the ZIP file
                zip_file.writestr(new_filename, output_data)
                
                # Add metadata
                size_reduction = input_size - output_size
                size_reduction_percent = (size_reduction / input_size * 100) if input_size > 0 else 0
                
                metadata.append({
                    "filename": image.filename,
                    "converted_filename": new_filename,
                    "status": "success",
                    "original_size": input_size,
                    "converted_size": output_size,
                    "size_reduction": size_reduction,
                    "size_reduction_percent": round(size_reduction_percent, 2)
                })
                
            except Exception as e:
                metadata.append({
                    "filename": image.filename,
                    "status": "failed",
                    "error": str(e)
                })
                
        # Add the metadata as a JSON file
        import json
        zip_file.writestr("conversion_metadata.json", json.dumps(metadata, indent=2))
    
    # Prepare the ZIP file for download
    zip_buffer.seek(0)
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=converted_images_{timestamp}.zip",
            "X-Converted-Files-Count": str(len([m for m in metadata if m.get('status') == 'success'])),
            "X-Failed-Files-Count": str(len([m for m in metadata if m.get('status') == 'failed']))
        }
    )