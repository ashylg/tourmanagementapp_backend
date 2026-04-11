from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Itinerary as DBItinerary
from src.models.itinerary import ItineraryCreate, ItineraryUpdate, ItineraryResponse

router = APIRouter(prefix="/itineraries", tags=["itineraries"])

def _to_response(doc: DBItinerary) -> ItineraryResponse:
    return ItineraryResponse(
        id=doc.id,
        client_id=doc.client_id,
        client_name=doc.client_name,
        assigned_agent_id=doc.assigned_agent_id,
        date_of_travel=doc.date_of_travel,
        number_of_people=doc.number_of_people,
        duration_days=doc.duration_days,
        significant_sites=doc.significant_sites,
        hotel_budget=doc.hotel_budget,
        status=doc.status,
        internal_notes=doc.internal_notes,
        activities=doc.activities,
        audit_logs=doc.audit_logs,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )

@router.get("", response_model=List[ItineraryResponse])
async def list_itineraries(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBItinerary).order_by(DBItinerary.created_at.desc()))
    docs = result.scalars().all()
    return [_to_response(d) for d in docs]

@router.post("", response_model=ItineraryResponse, status_code=201)
async def create_itinerary(data: ItineraryCreate, session: AsyncSession = Depends(get_async_session)):
    db_item = DBItinerary(**data.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return _to_response(db_item)

@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(itinerary_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBItinerary).where(DBItinerary.id == itinerary_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Itinerary not found")
    return _to_response(doc)

@router.put("/{itinerary_id}", response_model=ItineraryResponse)
async def update_itinerary(itinerary_id: str, data: ItineraryUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBItinerary).where(DBItinerary.id == itinerary_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Itinerary not found")
        
    updates = data.model_dump(exclude_unset=True)
    if "activities" in updates:
        updates["activities"] = [act for act in updates["activities"]]
        
    for k, v in updates.items():
        setattr(doc, k, v)
        
    doc.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(doc)
    return _to_response(doc)

@router.delete("/{itinerary_id}", status_code=204)
async def delete_itinerary(itinerary_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBItinerary).where(DBItinerary.id == itinerary_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Itinerary not found")
        
    await session.delete(doc)
    await session.commit()
