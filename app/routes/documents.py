from fastapi import APIRouter, HTTPException
from app.models.summarizeRequest import SummarizeRequest
from app.services.summarize import summarize_text

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    """
    Process and return text summarization using Google's Gemini API.
    """
    return await summarize_text(
        text=request.text,
        max_length=request.max_length,
        min_length=request.min_length
    )