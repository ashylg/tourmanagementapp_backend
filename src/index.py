from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.routers import status
from src.db.database import Base, engine

# Create the database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}

# Include routers
api_router.include_router(status.router)
app.include_router(api_router)
