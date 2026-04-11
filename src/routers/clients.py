from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Client as DBClient
from src.models.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/clients", tags=["clients"])

def _to_response(doc: DBClient) -> ClientResponse:
    return ClientResponse(
        id=doc.id,
        first_name=doc.first_name,
        last_name=doc.last_name,
        email=doc.email,
        phone=doc.phone,
        nationality=doc.nationality,
        passport_number=doc.passport_number,
        assigned_agent_id=doc.assigned_agent_id,
        created_at=doc.created_at
    )

@router.get("", response_model=List[ClientResponse])
async def list_clients(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBClient).order_by(DBClient.created_at.desc()))
    docs = result.scalars().all()
    return [_to_response(d) for d in docs]

@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(data: ClientCreate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBClient).where(DBClient.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Client with this email already exists")
    db_item = DBClient(**data.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return _to_response(db_item)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBClient).where(DBClient.id == client_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Client not found")
    return _to_response(doc)

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, data: ClientUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBClient).where(DBClient.id == client_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Client not found")
        
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
        
    for k, v in updates.items():
        setattr(doc, k, v)
        
    await session.commit()
    await session.refresh(doc)
    return _to_response(doc)

@router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBClient).where(DBClient.id == client_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Client not found")
        
    await session.delete(doc)
    await session.commit()
