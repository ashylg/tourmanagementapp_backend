from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Guide as DBGuide
from src.models.guide import GuideCreate, GuideUpdate, GuideResponse

router = APIRouter(prefix="/guides", tags=["guides"])

def _to_response(doc: DBGuide) -> GuideResponse:
    return GuideResponse(
        id=doc.id,
        first_name=doc.first_name,
        last_name=doc.last_name,
        specialization=doc.specialization,
        email=doc.email,
        phone=doc.phone,
        created_at=doc.created_at
    )

@router.get("", response_model=List[GuideResponse])
async def list_guides(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBGuide).order_by(DBGuide.created_at.desc()))
    docs = result.scalars().all()
    return [_to_response(d) for d in docs]

@router.post("", response_model=GuideResponse, status_code=201)
async def create_guide(data: GuideCreate, session: AsyncSession = Depends(get_async_session)):
    db_item = DBGuide(**data.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return _to_response(db_item)

@router.get("/{guide_id}", response_model=GuideResponse)
async def get_guide(guide_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBGuide).where(DBGuide.id == guide_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Guide not found")
    return _to_response(doc)

@router.put("/{guide_id}", response_model=GuideResponse)
async def update_guide(guide_id: str, data: GuideUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBGuide).where(DBGuide.id == guide_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Guide not found")
        
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
        
    for k, v in updates.items():
        setattr(doc, k, v)
        
    await session.commit()
    await session.refresh(doc)
    return _to_response(doc)

@router.delete("/{guide_id}", status_code=204)
async def delete_guide(guide_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBGuide).where(DBGuide.id == guide_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Guide not found")
        
    await session.delete(doc)
    await session.commit()
