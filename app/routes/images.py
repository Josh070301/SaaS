from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import os
import shutil

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files simultaneously.
    Returns a list of successfully uploaded filenames.
    """
    uploaded_files = []
    for file in files:
        try:
            with open(f"uploads/{file.filename}", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append({"filename": file.filename, "status": "success"})
        except Exception as e:
            uploaded_files.append({"filename": file.filename, "status": "failed", "error": str(e)})
    
    return {"uploaded_files": uploaded_files}