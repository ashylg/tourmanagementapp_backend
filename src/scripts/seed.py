import asyncio
import os
import bcrypt
import math
from datetime import datetime, timezone, timedelta

from src.db.database import init_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.schema import User, Client, Tour, Guide, Booking, Itinerary, Settings

async def seed_database():
    print("Connecting to DB & Initializing Schema...")
    await init_db()

    async with AsyncSessionLocal() as session:
        print("Seeding Users...")
        # Add basic users if missing
        hashed = bcrypt.hashpw("Admin@1234".encode(), bcrypt.gensalt()).decode()
        u = User(email="admin@tourapp.com", username="AdminUser", role="Admin", hashed_password=hashed)
        session.add(u)
        
        print("Seeding Tours...")
        t1 = Tour(name="Alpine Express", destination="Switzerland", description="A beautiful 7-day hike through the Swiss Alps", duration_days=7, price=2500.0, max_capacity=15)
        t2 = Tour(name="Kyoto Cherry Blossoms", destination="Japan", description="Experience the magical Sakura season", duration_days=10, price=3800.0, max_capacity=12)
        session.add_all([t1, t2])
        
        print("Seeding Guides...")
        g1 = Guide(first_name="Marco", last_name="Rossi", email="marco@tourapp.com", phone="555-1010", specialization="Wine & History")
        g2 = Guide(first_name="Kenji", last_name="Sato", email="kenji@tourapp.com", phone="555-2020", specialization="Japanese Culture")
        session.add_all([g1, g2])

        print("Seeding Clients...")
        c1 = Client(first_name="John", last_name="Smith", email="jsmith@example.com", phone="+1 555-1234", nationality="USA", passport_number="US987654", assigned_agent_id="agent_123")
        c2 = Client(first_name="Sarah", last_name="Connor", email="sconnor@example.com", phone="+44 7700-900", nationality="UK", passport_number="UK123456", assigned_agent_id="agent_123")
        session.add_all([c1, c2])

        # Commit to flush IDs
        await session.commit()
        await session.refresh(c1)
        await session.refresh(c2)
        await session.refresh(t1)
        await session.refresh(t2)

        print("Seeding Itineraries (With JSONB structured payload)...")
        it1 = Itinerary(
            client_id=c1.id,
            client_name=f"{c1.first_name} {c1.last_name}",
            assigned_agent_id="agent_123",
            date_of_travel="2026-07-15",
            number_of_people=2,
            duration_days=7,
            significant_sites="Eiffel Tower, Louvre Museum, Versailles",
            hotel_budget=1500.0,
            status="Booked",
            internal_notes="Reviewed historical rates for Paris in July. Usually spikes 20%.",
            activities=[
                {"type": "Flight", "provider_name": "Air France AF100", "start_time": "06:00", "end_time": "14:30", "cost": 850.0, "confirmed": True, "notes": "Lands CDG Terminal 2"},
                {"type": "Hotel", "provider_name": "Le Meurice", "start_time": "16:15", "cost": 1800.0, "confirmed": True, "notes": "Check-in post 3PM"}
            ],
            audit_logs=[
                {"action": "Marked Booked", "agent_id": "agent_123", "agent_name": "Admin", "timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()}
            ]
        )
        
        it2 = Itinerary(
            client_id=c2.id,
            client_name=f"{c2.first_name} {c2.last_name}",
            assigned_agent_id="agent_123",
            date_of_travel="2026-09-01",
            number_of_people=4,
            duration_days=14,
            significant_sites="Mount Fuji, Kyoto Shrines",
            hotel_budget=3000.0,
            status="Rates & Costing",
            internal_notes="Call 5 hotels in Kyoto for family suite rates.",
            activities=[
                {"type": "Flight", "provider_name": "JAL 55", "start_time": "08:00", "cost": 2400.0},
            ],
            audit_logs=[]
        )
        session.add_all([it1, it2])

        print("Seeding Bookings...")
        b1 = Booking(client_id=c1.id, client_name=c1.first_name, tour_id=t1.id, tour_name=t1.name, tour_date="2026-07-15", amount=t1.price, status="confirmed")
        b2 = Booking(client_id=c2.id, client_name=c2.first_name, tour_id=t2.id, tour_name=t2.name, tour_date="2026-09-01", amount=t2.price, status="pending")
        session.add_all([b1, b2])

        await session.commit()
        print("DB Seed Complete! Embedded SQLite via SQLAlchemy is running perfectly.")

if __name__ == "__main__":
    asyncio.run(seed_database())
