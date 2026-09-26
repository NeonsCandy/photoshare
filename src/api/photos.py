from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from fastapi_limiter.depends import RateLimiter
from src.database.db import get_db
from src.database.models import User, Role
from src.schemas import PhotoResponse, PhotoUpdate
from src.services.auth import get_current_user, RoleChecker
from src.services.cloud_image import CloudImage
from src.repository import photos as repository_photos
from typing import List, Optional
import qrcode
import io
import cloudinary.uploader
from src.schemas import PhotoTransform


router = APIRouter(prefix="/photos", tags=["photos"])

@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    description: str = Form(None),
    tags: str = Form(""), 
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    public_id = f"photoshare/{current_user.username}_{uuid.uuid4()}"
    
    r = CloudImage.upload_photo(file.file, public_id)
    src_url = CloudImage.get_url(public_id, r)
    
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    photo = await repository_photos.create_photo(src_url, description, tag_list, current_user, db)
    return photo
@router.get("/search/", response_model=List[PhotoResponse])
async def search_photos(
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Пошук фотографій за описом"""
    photos = await repository_photos.search_photos(keyword, tag, offset, limit, db)
    return photos

@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    photo = await repository_photos.get_photo_by_id(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo

@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int, 
    body: PhotoUpdate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    photo = await repository_photos.update_photo_description(photo_id, body.description, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Photo not found or you don't have permission to edit it"
        )
    return photo
allow_admin = RoleChecker([Role.admin])

@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    photo = await repository_photos.get_photo_by_id(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    
    if photo.user_id != current_user.id and current_user.role not in [Role.admin, Role.moderator]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to delete this photo")
        
    await repository_photos.delete_photo(photo_id, db)
    return None

@router.post("/{photo_id}/transform")
async def transform_and_get_qr(
    photo_id: int, 
    body: PhotoTransform, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    photo = await repository_photos.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    try:
        public_id = photo.url.split('/upload/')[1].split('/', 1)[1].rsplit('.', 1)[0]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Cloudinary URL structure")

    transformation = []
    if body.width or body.height:
        transformation.append({"width": body.width, "height": body.height, "crop": body.crop})
    if body.effect:
        transformation.append({"effect": body.effect})
    transformed_url = cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(transformed_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_public_id = f"photoshare/qrcodes/{current_user.username}_{uuid.uuid4()}"
    r = cloudinary.uploader.upload(buf, public_id=qr_public_id)
    qr_url = cloudinary.CloudinaryImage(qr_public_id).build_url(version=r.get('version'))

    return {
        "photo_id": photo.id,
        "original_url": photo.url,
        "transformed_url": transformed_url,
        "qr_code_url": qr_url
    }