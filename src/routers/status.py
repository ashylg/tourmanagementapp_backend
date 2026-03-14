from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.status import StatusCheck, StatusCheckCreate
from src.models.domain import StatusCheckModel
from src.db.database import get_db

router = APIRouter(prefix="/status")

@router.post("")
async def create_status_check(input_data: StatusCheckCreate, db: Session = Depends(get_db)):
    try:
        # Create Pydantic model
        status_data = StatusCheck(client_name=input_data.client_name)
        
        # Create SQLAlchemy ORM model
        db_status = StatusCheckModel(
            id=status_data.id,
            client_name=status_data.client_name,
            timestamp=status_data.timestamp
        )
        
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        
        # Return response using the isoformat for compatibility
        return {
            "id": db_status.id,
            "client_name": db_status.client_name,
            "timestamp": db_status.timestamp.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def get_status_checks(db: Session = Depends(get_db)):
    try:
        results = db.query(StatusCheckModel).order_by(StatusCheckModel.timestamp.desc()).all()
        # Convert ORM objects back to a serializable format for FastAPI
        return [
            {
                "id": r.id,
                "client_name": r.client_name,
                "timestamp": r.timestamp.isoformat()
            }
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
