from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ItineraryCreate(BaseModel):
    client_id: str
    client_name: str
    assigned_agent_id: Optional[str] = None
    date_of_travel: str
    number_of_people: int = 1
    duration_days: int = 1
    significant_sites: Optional[str] = None
    hotel_budget: float = 0.0
    status: str = "Initial Inquiry"
    internal_notes: Optional[str] = None
    activities: Optional[List[dict]] = []
    audit_logs: Optional[List[dict]] = []

class ItineraryUpdate(BaseModel):
    status: Optional[str] = None
    internal_notes: Optional[str] = None
    activities: Optional[List[dict]] = None
    audit_logs: Optional[List[dict]] = None

class ItineraryResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    assigned_agent_id: Optional[str]
    date_of_travel: str
    number_of_people: int
    duration_days: int
    significant_sites: Optional[str]
    hotel_budget: float
    status: str
    internal_notes: Optional[str]
    activities: Optional[List[dict]]
    audit_logs: Optional[List[dict]]
    created_at: datetime
    updated_at: datetime
