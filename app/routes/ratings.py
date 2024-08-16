# app/routes/ratings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert
from app import models, schemas, utils
from app.database import database
from typing import List

router = APIRouter()


async def get_current_user(token: str = Depends(utils.oauth2_scheme)):
    return await utils.get_current_user(token)


@router.post("/movies/{movie_id}/ratings/", response_model=schemas.Rating)
async def create_rating(movie_id: int, rating: schemas.RatingCreate,
                        current_user: models.User = Depends(get_current_user)):
    query = insert(models.Rating).values(
        rating=rating.rating,
        movie_id=movie_id,
        user_id=current_user.id
    )
    last_record_id = await database.execute(query)
    return {**rating.dict(), "id": last_record_id, "movie_id": movie_id, "user_id": current_user.id}


@router.get("/movies/{movie_id}/ratings/", response_model=List[schemas.Rating])
async def read_ratings(movie_id: int, skip: int = 0, limit: int = 10):
    query = select(models.Rating).where(models.Rating.movie_id == movie_id).offset(skip).limit(limit)
    return await database.fetch_all(query)
