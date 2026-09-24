from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas import CommentBase, CommentResponse
from src.services.auth import get_current_user
from src.repository import comments as repository_comments
from src.repository import photos as repository_photos

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/{photo_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(photo_id: int, body: CommentBase, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    photo = await repository_photos.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    
    return await repository_comments.create_comment(photo_id, body.text, current_user, db)

@router.get("/{photo_id}", response_model=List[CommentResponse])
async def read_comments(photo_id: int, offset: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await repository_comments.get_comments_by_photo(photo_id, offset, limit, db)

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, body: CommentBase, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")
        
    return await repository_comments.update_comment(comment, body.text, db)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id and current_user.role not in [Role.admin, Role.moderator]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to delete this comment")
        
    await repository_comments.delete_comment(comment, db)
    return None