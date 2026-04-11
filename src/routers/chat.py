from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import ChatMessage as DBChatMessage
from src.models.chat import ChatMessageResponse, ChatMessageCreate
from src.routers.auth import get_current_user
from src.models.user import UserInDB

router = APIRouter(prefix="/chat", tags=["chat"])

def _to_response(doc: DBChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=doc.id,
        itinerary_id=doc.itinerary_id,
        sender_id=doc.sender_id,
        sender_name=doc.sender_name,
        message=doc.message,
        timestamp=doc.timestamp
    )

@router.get("/{itinerary_id}", response_model=List[ChatMessageResponse])
async def get_messages(itinerary_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(DBChatMessage)
        .where(DBChatMessage.itinerary_id == itinerary_id)
        .order_by(DBChatMessage.timestamp.asc())
    )
    docs = result.scalars().all()
    return [_to_response(d) for d in docs]

@router.post("", response_model=ChatMessageResponse)
async def post_message(
    data: ChatMessageCreate, 
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    db_item = DBChatMessage(
        itinerary_id=data.itinerary_id,
        sender_id=current_user.id,
        sender_name=current_user.username,
        message=data.message
    )
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return _to_response(db_item)
