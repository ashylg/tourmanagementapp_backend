import os
import bcrypt
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_async_session, init_db, AsyncSessionLocal
from src.db.schema import Tour, Booking, Client, Guide
from src.routers import auth, tours, clients, guides, bookings, itineraries, chat, analytics, users, settings

load_dotenv(Path(__file__).parent.parent / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="Tour Management API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(tours.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(guides.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(itineraries.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


@app.get("/api")
async def root():
    return {"message": "JourneyCraft Tour Management API v2.0 — PostgreSQL/SQLAlchemy"}


# ─── Dashboard Stats ──────────────────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats(session: AsyncSession = Depends(get_async_session)):
    total_tours = len((await session.execute(select(Tour))).scalars().all())
    all_bookings = (await session.execute(select(Booking))).scalars().all()
    total_clients = len((await session.execute(select(Client))).scalars().all())
    total_guides = len((await session.execute(select(Guide))).scalars().all())

    confirmed_bookings = [b for b in all_bookings if b.status == "confirmed"]
    total_revenue = sum(b.amount for b in confirmed_bookings)

    return {
        "tours": {"total": total_tours, "active": total_tours},
        "bookings": {
            "total": len(all_bookings),
            "confirmed": len(confirmed_bookings),
            "pending": len([b for b in all_bookings if b.status == "pending"]),
            "cancelled": len([b for b in all_bookings if b.status == "cancelled"])
        },
        "clients": {"total": total_clients},
        "guides": {"total": total_guides, "available": total_guides},
        "revenue": {"total": round(total_revenue, 2)},
    }


# ─── Startup ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    await init_db()

    # Import schema here to ensure tables are loaded before create_all
    from src.db.schema import User

    enabled = os.environ.get("SUPERUSER_ENABLED", "false").lower() == "true"
    if not enabled:
        logger.info("Superuser auto-seed disabled.")
        return

    email = os.environ.get("SUPERUSER_EMAIL", "admin@tourapp.com")
    username = os.environ.get("SUPERUSER_USERNAME", "admin")
    password = os.environ.get("SUPERUSER_PASSWORD", "Admin@1234")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            logger.info(f"Superuser '{username}' already exists — skipping.")
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_admin = User(email=email, username=username, hashed_password=hashed, role="Admin", is_active=True)
        session.add(new_admin)
        await session.commit()
        logger.info(f"✅ Superuser '{username}' ({email}) created.")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("App shutting down.")
