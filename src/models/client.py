from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    assigned_agent_id: Optional[str] = None

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    assigned_agent_id: Optional[str] = None

class ClientResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    nationality: Optional[str]
    passport_number: Optional[str]
    assigned_agent_id: Optional[str]
    created_at: datetime
