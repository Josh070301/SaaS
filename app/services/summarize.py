import os
import requests
from fastapi import HTTPException

async def summarize_text(text: str, max_length: int = 150, min_length: int = 30):
    """
    Summarize text using Google's Gemini API.
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
                            "text": f"Summarize the following text in about {max_length} words. Ensure the summary is between {min_length} and {max_length} words:\n\n{text}. Just provide the summary without any additional commentary and just plain text."
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
            "original_length": len(text),
            "summary_length": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")