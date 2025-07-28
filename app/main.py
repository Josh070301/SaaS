from fastapi import FastAPI, File, UploadFile, Body, HTTPException
from typing import List
import shutil
import os
import requests
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

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
    Process and return text summarization using Google's Gemini API.
    """
    # Get API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not found")
    
    try:
        # Gemini API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Prepare request payload for Gemini
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Summarize the following text in about {request.max_length} words. Ensure the summary is between {request.min_length} and {request.max_length} words:\n\n{request.text}. Just provide the summary without any additional commentary and just plain text."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            'X-goog-api-key': api_key
        }
        
        response = requests.post(
            url, 
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # Extract summary from Gemini response
        summary = response_data["candidates"][0]["content"]["parts"][0]["text"]
        
        return {
            "summary": summary,
            "original_length": len(request.text),
            "summary_length": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")