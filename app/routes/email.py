from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.emailService import send_email

router = APIRouter(prefix="/email", tags=["email"])

class EmailRequest(BaseModel):
    to: str = Field(..., description="Email address of the recipient")
    subject: str = Field(..., description="Subject of the email")
    content: str = Field(..., description="HTML content of the email")

@router.post("/send")
async def send_email_route(request: EmailRequest):
    """
    Send an email to the specified recipient.
    
    Requires:
    - to: Email address of the recipient
    - subject: Subject of the email
    - content: Main message content
    """
    # Create template_vars dictionary from request
    template_vars = {
        "main_message": request.content
    }
    
    return await send_email(
        to=request.to,
        subject=request.subject,
        template_vars=template_vars
    )