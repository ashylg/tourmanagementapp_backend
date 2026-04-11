from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class GuideCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    specialization: Optional[str] = None

class GuideUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None

class GuideResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    specialization: Optional[str]
    email: str
    phone: str
    created_at: datetime
