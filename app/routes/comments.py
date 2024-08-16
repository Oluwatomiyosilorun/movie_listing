# app/routes/comments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, delete
from app import models, schemas, utils
from app.database import database
from datetime import datetime
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


async def get_current_user(token: str = Depends(utils.oauth2_scheme)):
    return await utils.get_current_user(token)


@router.post("/{movie_id}", response_model=schemas.Comment)
async def create_comment(
        movie_id: int,
        comment: schemas.CommentCreate,
        current_user: models.User = Depends(get_current_user)
):
    query = models.Comment.__table__.insert().values(
        content=comment.content,
        movie_id=movie_id,
        user_id=current_user.id,
        parent_comment_id=comment.parent_comment_id
    )

    last_record_id = await database.execute(query)

    return schemas.Comment(
        id=last_record_id,
        content=comment.content,
        movie_id=movie_id,
        user_id=current_user.id,
        parent_comment_id=comment.parent_comment_id,
        created_at=datetime.utcnow()
    )


@router.get("/{movie_id}", response_model=List[schemas.Comment])
async def read_comments(movie_id: int, skip: int = 0, limit: int = 10):
    try:
        query = select(
            models.Comment.id,
            models.Comment.content,
            models.Comment.movie_id,
            models.Comment.user_id,
            models.Comment.parent_comment_id,
            models.Comment.created_at
        ).where(models.Comment.movie_id == movie_id).offset(skip).limit(limit)

        comments = await database.fetch_all(query)

        return [
            schemas.Comment(
                id=comment["id"],
                content=comment["content"],
                movie_id=comment["movie_id"],
                user_id=comment["user_id"],
                parent_comment_id=comment["parent_comment_id"],
                created_at=comment["created_at"] or datetime.utcnow()
            )
            for comment in comments
        ]
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{comment_id}", response_model=dict)
async def delete_comment(comment_id: int, current_user: models.User = Depends(get_current_user)):
    query = select(models.Comment).where(models.Comment.id == comment_id)
    db_comment = await database.fetch_one(query)

    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if db_comment["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    delete_query = delete(models.Comment).where(models.Comment.id == comment_id)
    await database.execute(delete_query)

    # Return a success message
    return {"message": "Comment deleted successfully"}
