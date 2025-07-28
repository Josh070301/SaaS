from pydantic import BaseModel

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 30