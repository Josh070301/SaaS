from fastapi import FastAPI, File, UploadFile, Body, HTTPException
from typing import List
import shutil
import os
from pydantic import BaseModel

app = FastAPI()

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Initialize the summarization pipeline with error handling
try:
    from transformers import pipeline
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summarization_available = True
except (ImportError, NameError) as e:
    print(f"Warning: Summarization not available - {str(e)}")
    summarization_available = False

# Dto request model for summarization
class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 30

@app.post("/upload/")
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

@app.post("/summarize/")
async def summarize(request: SummarizeRequest):
    """
    Process and return the full summarization of the input text using transformers.
    Takes the text in the request body along with optional max_length and min_length parameters.
    """
    if not summarization_available:
        raise HTTPException(
            status_code=503, 
            detail="Summarization service is not available. Please install PyTorch: 'pip install torch'"
        )
        
    text = request.text
    
    # Use the transformers pipeline for summarization
    try:
        summary_result = summarizer(text, 
                                max_length=request.max_length, 
                                min_length=request.min_length, 
                                do_sample=False)
        
        # Extract the summary text from the result
        summary = summary_result[0]['summary_text']
            
        return {
            "summary": summary, 
            "original_length": len(text), 
            "summary_length": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")