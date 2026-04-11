from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.db.schema import Itinerary

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics(session: AsyncSession = Depends(get_async_session)):
    
    result = await session.execute(select(Itinerary))
    itineraries = result.scalars().all()
    
    total_inquiries = len(itineraries)
    draft_sent = sum(1 for i in itineraries if i.status in ["Draft 1 Sent", "Rates & Costing", "Draft 2 Sent", "Final Confirmed", "Booked"])
    booked = sum(1 for i in itineraries if i.status == "Booked")
    
    funnel = {
        "inquiries": total_inquiries,
        "drafts": draft_sent,
        "booked": booked,
        "conversion_rate": round(booked / total_inquiries * 100, 1) if total_inquiries > 0 else 0
    }
    
    revenue_by_type = {}
    for it in itineraries:
        if it.status == "Booked" and it.activities:
             for act in it.activities:
                 # Check if act is a dict
                 if not isinstance(act, dict):
                     continue
                 act_type = act.get("type", "Unknown")
                 act_cost = float(act.get("cost", 0))
                 revenue_by_type[act_type] = revenue_by_type.get(act_type, 0) + act_cost
                 
    total_revenue = sum(revenue_by_type.values())
    
    return {
        "funnel": funnel,
        "revenue_by_type": revenue_by_type,
        "total_revenue": total_revenue
    }
