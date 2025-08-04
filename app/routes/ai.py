from fastapi import APIRouter, HTTPException
from app.models.summarizeRequest import SummarizeRequest
from app.services.summarize import summarize_text

from pydantic import BaseModel
from app.services.frontEndBasedAI import getFrontEndBasedAI

class PortfolioRequest(BaseModel):
    text: str

router = APIRouter(prefix="/ai", tags=["ai"])

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
    
@router.post("/front-end-based")
async def portfolio(request: PortfolioRequest):
    """
    Process and return text from portfolio request.
    """
    return await getFrontEndBasedAI(
        text=request.text
    )