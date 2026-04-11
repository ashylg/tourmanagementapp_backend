import os
import bcrypt
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.future import select

from src.db.database import get_async_session
from src.db.schema import User
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import UserInDB, UserCreate, UserResponse, Token, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = os.environ.get("JWT_SECRET", "fallback-secret")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)) -> UserInDB:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise exc
    return UserInDB(id=user.id, email=user.email, username=user.username,
                    role=user.role, company_id=user.company_id, is_active=user.is_active, 
                    hashed_password=user.hashed_password, created_at=user.created_at)

def _user_response(user: UserInDB) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, username=user.username,
                        role=user.role, company_id=user.company_id, is_active=user.is_active)

@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, session: AsyncSession = Depends(get_async_session)):
    
    r1 = await session.execute(select(User).where(User.email == data.email))
    if r1.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
        
    r2 = await session.execute(select(User).where(User.username == data.username))
    if r2.scalar_one_or_none():
        raise HTTPException(400, "Username already taken")
        
    new_user = User(
        email=data.email, 
        username=data.username, 
        hashed_password=hash_password(data.password),
        role="View-Only" # Enforce RBAC
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    u = UserInDB(id=new_user.id, email=new_user.email, username=new_user.username,
                    role=new_user.role, company_id=new_user.company_id, is_active=new_user.is_active, 
                    hashed_password=new_user.hashed_password, created_at=new_user.created_at)
    return _user_response(u)

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(User).where(User.email == credentials.email))
    doc = res.scalar_one_or_none()
    if not doc or not verify_password(credentials.password, doc.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    
    if not doc.is_active:
        raise HTTPException(403, "Account is disabled")
    token = create_access_token({"sub": doc.id})
    
    u = UserInDB(id=doc.id, email=doc.email, username=doc.username,
                    role=doc.role, company_id=doc.company_id, is_active=doc.is_active, 
                    hashed_password=doc.hashed_password, created_at=doc.created_at)
    return Token(access_token=token, token_type="bearer", user=_user_response(u))

@router.post("/token")
async def token_endpoint(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(User).where(User.email == form.username))
    doc = res.scalar_one_or_none()
    if not doc or not verify_password(form.password, doc.hashed_password):
        raise HTTPException(401, "Incorrect credentials")
    token = create_access_token({"sub": doc.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def me(current_user: UserInDB = Depends(get_current_user)):
    return _user_response(current_user)
