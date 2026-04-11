from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TourCreate(BaseModel):
    name: str
    description: Optional[str] = None
    destination: str
    duration_days: int
    price: float
    max_capacity: int

class TourUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    price: Optional[float] = None
    max_capacity: Optional[int] = None

class TourResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    destination: str
    duration_days: int
    price: float
    max_capacity: int
    created_at: datetime
