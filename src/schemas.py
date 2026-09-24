from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from src.database.models import Role
from typing import List, Optional


class PhotoTransform(BaseModel):
    width: Optional[int] = Field(None, description="Ширина в пікселях (наприклад 500)")
    height: Optional[int] = Field(None, description="Висота в пікселях (наприклад 500)")
    crop: str = Field("fill", description="Тип обрізки: fill, scale, crop, thumb")
    effect: Optional[str] = Field(None, description="Ефект: grayscale, sepia, blur:100, cartoonify")
    
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=255)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role
    avatar: str | None

    class Config:
        from_attributes = True  

class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PhotoResponse(BaseModel):
    id: int
    url: str
    description: Optional[str]
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True
class PhotoUpdate(BaseModel):
    description: str

class CommentBase(BaseModel):
    text: str = Field(min_length=1, max_length=255)

class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    photo_id: int

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str]
    role: str
    created_at: datetime
    photos_count: int = 0

    class Config:
        from_attributes = True