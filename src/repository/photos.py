from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Photo, Tag, User

async def get_or_create_tags(tag_names: list[str], db: AsyncSession):
    """Обробляє список тегів: знаходить існуючі"""
    tags = []
    for name in tag_names[:5]:
        name = name.strip().lower()
        if not name:
            continue
            
        stmt = select(Tag).where(Tag.name == name)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()
        
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags

async def create_photo(url: str, description: str, tags: list[str], user: User, db: AsyncSession):
    """Зберігає фото в базу даних"""
    db_tags = await get_or_create_tags(tags, db)
    
    photo = Photo(
        url=url, 
        description=description, 
        user_id=user.id, 
        tags=db_tags
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo

async def get_photo_by_id(photo_id: int, db: AsyncSession):
    """Повертає фотографію за її ID"""
    stmt = select(Photo).where(Photo.id == photo_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_photo_description(photo_id: int, description: str, user: User, db: AsyncSession):
    """Оновлює опис фотографії"""
    photo = await get_photo_by_id(photo_id, db)
    if photo and photo.user_id == user.id:
        photo.description = description
        await db.commit()
        await db.refresh(photo)
        return photo
    return None

async def delete_photo(photo_id: int, db: AsyncSession):
    """Видаляє фотографію з бази даних"""
    photo = await get_photo_by_id(photo_id, db)
    if photo:
        await db.delete(photo)
        await db.commit()
    return photo
async def search_photos(keyword: str | None, tag: str | None, offset: int, limit: int, db: AsyncSession):
    """Шукаємо фото за ключовим словом в описі"""
    stmt = select(Photo)
    if keyword:
        stmt = stmt.where(Photo.description.ilike(f"%{keyword}%"))
    if tag:
        stmt = stmt.where(Photo.tags.any(Tag.name == tag.strip().lower()))
    stmt = stmt.offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()