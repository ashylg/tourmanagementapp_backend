import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    default_currency: str = "INR"
    default_country: str = "India"
    tax_rate_percent: float = 18.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SettingsUpdate(BaseModel):
    default_currency: str
    default_country: str
    tax_rate_percent: float
