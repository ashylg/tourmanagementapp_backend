import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class UserInDB(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    hashed_password: str
    role: str = "Admin" # Admin, Sales Agent, View-Only
    company_id: str = "default_company"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    role: str = "Admin"
    company_id: str = "default_company"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    role: str
    company_id: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    email: str
    password: str
