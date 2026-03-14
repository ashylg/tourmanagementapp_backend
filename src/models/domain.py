from sqlalchemy import Column, String, DateTime
import uuid
from datetime import datetime, timezone
from src.db.database import Base

class StatusCheckModel(Base):
    __tablename__ = "status_checks"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    client_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
