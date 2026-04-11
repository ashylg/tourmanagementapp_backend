from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import User
from src.models.user import UserInDB, UserResponse
from src.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class UserUpdateRole(BaseModel):
    role: str

def _user_response(u: User) -> UserResponse:
    return UserResponse(id=u.id, email=u.email, username=u.username, role=u.role, company_id=u.company_id, is_active=u.is_active)

@router.get("", response_model=List[UserResponse])
async def list_users(current_user: UserInDB = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    result = await session.execute(select(User).where(User.company_id == current_user.company_id))
    users = result.scalars().all()
    return [_user_response(u) for u in users]

@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(user_id: str, data: UserUpdateRole, current_user: UserInDB = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    result = await session.execute(select(User).where(User.id == user_id, User.company_id == current_user.company_id))
    user_doc = result.scalar_one_or_none()
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_doc.role = data.role
    await session.commit()
    await session.refresh(user_doc)
    return _user_response(user_doc)

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: UserInDB = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    result = await session.execute(select(User).where(User.id == user_id, User.company_id == current_user.company_id))
    user_doc = result.scalar_one_or_none()
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
        
    await session.delete(user_doc)
    await session.commit()
    return {"status": "deleted"}
