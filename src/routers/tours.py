from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Tour as DBTour
from src.models.tour import TourCreate, TourUpdate, TourResponse

router = APIRouter(prefix="/tours", tags=["tours"])

def _to_response(doc: DBTour) -> TourResponse:
    return TourResponse(
        id=doc.id,
        name=doc.name,
        description=doc.description,
        destination=doc.destination,
        duration_days=doc.duration_days,
        price=doc.price,
        max_capacity=doc.max_capacity,
        created_at=doc.created_at
    )

@router.get("", response_model=List[TourResponse])
async def list_tours(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBTour).order_by(DBTour.created_at.desc()))
    docs = result.scalars().all()
    return [_to_response(d) for d in docs]

@router.post("", response_model=TourResponse, status_code=201)
async def create_tour(data: TourCreate, session: AsyncSession = Depends(get_async_session)):
    db_item = DBTour(**data.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return _to_response(db_item)

@router.get("/{tour_id}", response_model=TourResponse)
async def get_tour(tour_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBTour).where(DBTour.id == tour_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Tour not found")
    return _to_response(doc)

@router.put("/{tour_id}", response_model=TourResponse)
async def update_tour(tour_id: str, data: TourUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBTour).where(DBTour.id == tour_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Tour not found")
        
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
        
    for k, v in updates.items():
        setattr(doc, k, v)
        
    await session.commit()
    await session.refresh(doc)
    return _to_response(doc)

@router.delete("/{tour_id}", status_code=204)
async def delete_tour(tour_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBTour).where(DBTour.id == tour_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Tour not found")
        
    await session.delete(doc)
    await session.commit()
