import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, JSON
from src.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Admin")
    company_id = Column(String, index=True, default="default_company")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=generate_uuid)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    passport_number = Column(String, nullable=True)
    assigned_agent_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Tour(Base):
    __tablename__ = "tours"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    destination = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Guide(Base):
    __tablename__ = "guides"
    id = Column(String, primary_key=True, default=generate_uuid)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    specialization = Column(String, nullable=True)
    email = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, index=True, nullable=False)
    client_name = Column(String, nullable=False)
    tour_id = Column(String, index=True, nullable=False)
    tour_name = Column(String, nullable=False)
    tour_date = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Itinerary(Base):
    __tablename__ = "itineraries"
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, index=True, nullable=False)
    client_name = Column(String, nullable=False)
    assigned_agent_id = Column(String, index=True, nullable=True)
    date_of_travel = Column(String, nullable=False)
    number_of_people = Column(Integer, default=1)
    duration_days = Column(Integer, default=1)
    significant_sites = Column(String, nullable=True)
    hotel_budget = Column(Float, default=0.0)
    status = Column(String, default="Initial Inquiry")
    internal_notes = Column(Text, nullable=True)
    activities = Column(JSON, default=list)
    audit_logs = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=generate_uuid)
    itinerary_id = Column(String, index=True, nullable=False)
    sender_id = Column(String, nullable=False)
    sender_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Settings(Base):
    __tablename__ = "settings"
    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, index=True, nullable=False, unique=True)
    default_currency = Column(String, default="INR")
    default_country = Column(String, default="India")
    tax_rate_percent = Column(Float, default=18.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
