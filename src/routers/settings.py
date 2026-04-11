from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Settings as DBSettings
from src.models.user import UserInDB
from src.routers.auth import get_current_user
from src.models.settings import Settings, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=Settings)
async def get_settings(current_user: UserInDB = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DBSettings).where(DBSettings.company_id == current_user.company_id))
    settings_doc = result.scalar_one_or_none()
    
    if not settings_doc:
        # Auto-initialize default settings for company if missing
        new_settings = DBSettings(company_id=current_user.company_id)
        session.add(new_settings)
        await session.commit()
        await session.refresh(new_settings)
        return Settings(id=new_settings.id, company_id=new_settings.company_id, default_currency=new_settings.default_currency,
                        default_country=new_settings.default_country, tax_rate_percent=new_settings.tax_rate_percent, 
                        updated_at=new_settings.updated_at)
                        
    return Settings(id=settings_doc.id, company_id=settings_doc.company_id, default_currency=settings_doc.default_currency,
                        default_country=settings_doc.default_country, tax_rate_percent=settings_doc.tax_rate_percent, 
                        updated_at=settings_doc.updated_at)

@router.put("", response_model=Settings)
async def update_settings(data: SettingsUpdate, current_user: UserInDB = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    result = await session.execute(select(DBSettings).where(DBSettings.company_id == current_user.company_id))
    settings_doc = result.scalar_one_or_none()
    
    if not settings_doc:
        settings_doc = DBSettings(company_id=current_user.company_id, **data.model_dump())
        session.add(settings_doc)
    else:
        for k, v in data.model_dump().items():
            setattr(settings_doc, k, v)
        settings_doc.updated_at = datetime.now(timezone.utc)
        
    await session.commit()
    await session.refresh(settings_doc)
    
    return Settings(id=settings_doc.id, company_id=settings_doc.company_id, default_currency=settings_doc.default_currency,
                        default_country=settings_doc.default_country, tax_rate_percent=settings_doc.tax_rate_percent, 
                        updated_at=settings_doc.updated_at)
