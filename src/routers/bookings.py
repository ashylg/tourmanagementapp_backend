from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Booking as DBBooking, Client as DBClient, Tour as DBTour
from src.models.booking import BookingCreate, BookingUpdate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])

def _to_response(doc: DBBooking) -> BookingResponse:
    return BookingResponse(
        id=doc.id,
        client_id=doc.client_id,
        client_name=doc.client_name,
        tour_id=doc.tour_id,
        tour_name=doc.tour_name,
        tour_date=doc.tour_date,
        amount=doc.amount,
        status=doc.status,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )

@router.get("", response_model=List[BookingResponse])
async def list_bookings(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBBooking).order_by(DBBooking.created_at.desc()))
    docs = result.scalars().all()
    return [_to_response(d) for d in docs]

@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(data: BookingCreate, session: AsyncSession = Depends(get_async_session)):
    # Validate client and tour exist
    c_res = await session.execute(select(DBClient).where(DBClient.id == data.client_id))
    client = c_res.scalar_one_or_none()
    if not client:
        raise HTTPException(400, "Invalid client_id")
        
    t_res = await session.execute(select(DBTour).where(DBTour.id == data.tour_id))
    tour = t_res.scalar_one_or_none()
    if not tour:
        raise HTTPException(400, "Invalid tour_id")

    payload = data.model_dump()
    payload["client_name"] = f"{client.first_name} {client.last_name}"
    payload["tour_name"] = tour.name
    if not payload.get("amount") and tour.price is not None:
        payload["amount"] = tour.price
    elif not payload.get("amount"):
        payload["amount"] = 0.0

    db_item = DBBooking(**payload)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return _to_response(db_item)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBBooking).where(DBBooking.id == booking_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Booking not found")
    return _to_response(doc)

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: str, data: BookingUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBBooking).where(DBBooking.id == booking_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Booking not found")
        
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
        
    for k, v in updates.items():
        setattr(doc, k, v)
        
    doc.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(doc)
    return _to_response(doc)

@router.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBBooking).where(DBBooking.id == booking_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Booking not found")
        
    await session.delete(doc)
    await session.commit()
