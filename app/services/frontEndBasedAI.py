import os
import requests
from fastapi import HTTPException

async def getFrontEndBasedAI(text: str):
    # Get API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not found")
    
    try:
        # Gemini API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Prepare request payload for Gemini
        
        prompt_text = f"{text}, You can use them in your response. If the question is not within the provided information. If the question is not within the provided information. response that is not your coverage. Do not be Joshua Laude, just be an AI that knows him. Do not response like you are Joshua Laude. You can use new line spaces or bold texts to make the response more readable and organized."


        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt_text
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
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API failed: {str(e)}")