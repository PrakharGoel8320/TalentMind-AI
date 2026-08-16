from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.session import get_db
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
        
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        role=UserRole.RECRUITER
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    token = create_access_token(subject=str(new_user.id), role=new_user.role.value)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role.value,
            "name": request.name
        }
    }

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    token = create_access_token(subject=str(user.id), role=user.role.value)
    
    # We don't store "name" explicitly in the base User model in some setups, but assuming we just use email prefix if missing
    name = getattr(user, 'name', user.email.split("@")[0].title())
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "name": name
        }
    }
