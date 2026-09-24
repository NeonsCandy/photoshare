from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, Photo
from src.schemas import UserCreate  


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """Шукає користувача в базі за email"""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(body: UserCreate, db: AsyncSession) -> User:
    """Створює нового користувача в базі"""
    new_user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        avatar=None
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_profile(username: str, db: AsyncSession):
    """Шукає користувача за його юзернеймом"""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def count_user_photos(user_id: int, db: AsyncSession) -> int:
    """Рахує кількість світлин, які завантажив користувач"""
    stmt = select(func.count(Photo.id)).where(Photo.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar() or 0

async def update_avatar(email: str, url: str, db: AsyncSession) -> User:
    """Оновлює посилання на аватарку користувача"""
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user