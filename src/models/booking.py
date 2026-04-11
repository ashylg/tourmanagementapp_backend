import uuid
from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel

BookingStatus = Literal["pending", "confirmed", "cancelled"]

class BookingCreate(BaseModel):
    tour_id: str
    client_id: str
    tour_date: str
    amount: Optional[float] = None

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    amount: Optional[float] = None

class BookingResponse(BaseModel):
    id: str
    tour_id: str
    client_id: str
    client_name: str
    tour_name: str
    tour_date: str
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime
