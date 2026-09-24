from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Comment, User
async def create_comment(photo_id: int, text: str, user: User, db: AsyncSession):
    new_comment = Comment(text=text, photo_id=photo_id, user_id=user.id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment
async def get_comments_by_photo(photo_id: int, offset: int, limit: int, db: AsyncSession):
    stmt = select(Comment).where(Comment.photo_id == photo_id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
async def get_comment_by_id(comment_id: int, db: AsyncSession):
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
async def update_comment(comment: Comment, text: str, db: AsyncSession):
    comment.text = text
    await db.commit()
    await db.refresh(comment)
    return comment
async def delete_comment(comment: Comment, db: AsyncSession):
    await db.delete(comment)
    await db.commit()