from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserProfileResponse
from src.services.auth import get_current_user
from src.services.cloud_image import CloudImage
from src.repository import users as repository_users

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{username}", response_model=UserProfileResponse)
async def read_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_profile(username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    photos_count = await repository_users.count_user_photos(user.id, db)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "role": user.role.name if hasattr(user.role, 'name') else str(user.role),
        "created_at": user.created_at,
        "photos_count": photos_count
    }

@router.patch("/avatar", response_model=UserProfileResponse)
async def update_avatar_image(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    public_id = f"photoshare/avatars/{current_user.username}"
    r = CloudImage.upload_photo(file.file, public_id)
    src_url = CloudImage.get_url(public_id, r)
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    photos_count = await repository_users.count_user_photos(user.id, db)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "role": user.role.name if hasattr(user.role, 'name') else str(user.role),
        "created_at": user.created_at,
        "photos_count": photos_count
    }