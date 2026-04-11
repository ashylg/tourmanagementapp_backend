from datetime import datetime
from pydantic import BaseModel

class ChatMessageCreate(BaseModel):
    itinerary_id: str
    message: str

class ChatMessageResponse(BaseModel):
    id: str
    itinerary_id: str
    sender_id: str
    sender_name: str
    message: str
    timestamp: datetime
