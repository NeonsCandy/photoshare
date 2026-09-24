from unittest import result

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.database.models import User, Role
from src.schemas import UserCreate, UserResponse, TokenModel
from src.repository import users as repository_users
from src.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreate, db: AsyncSession = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    is_first_user = result.scalar_one_or_none() is None
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    
    if is_first_user:
        new_user.role = Role.admin
        await db.commit()
        await db.refresh(new_user)
        
    return new_user

@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

    @app.get("/api/users/me")
    async def read_users_me(current_user: User = Depends(get_current_user)):
        return current_user

    allow_admin = RoleChecker([Role.admin])

    @app.delete("/api/photos/{photo_id}")
    async def delete_photo_by_admin(photo_id: int, current_user: User = Depends(allow_admin)):
        return {"message": "Фото видалено адміном"}