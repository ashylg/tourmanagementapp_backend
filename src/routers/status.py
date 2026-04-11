from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["status"])

@router.get("")
async def health_check():
    return {"status": "ok", "engine": "SQLAlchemy/SQLite"}
