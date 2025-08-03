from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.portfolio import getPortfolio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

class PortfolioRequest(BaseModel):
    text: str

@router.post("/ai", include_in_schema=False)
async def portfolio(request: PortfolioRequest):
    """
    Process and return text from portfolio request.
    """
    return await getPortfolio(
        text=request.text
    )