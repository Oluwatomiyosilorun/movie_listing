# app/routes/movies.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete, update
from app import models, schemas, utils
from app.database import database
from datetime import datetime
from typing import List
import logging

router = APIRouter()

logger = logging.getLogger("uvicorn.error")


async def get_current_user(token: str = Depends(utils.oauth2_scheme)):
    return await utils.get_current_user(token)


@router.post("/movies/", response_model=schemas.Movie)
async def create_movie(movie: schemas.MovieCreate, current_user: models.User = Depends(utils.get_current_user)):
    release_date = movie.release_date or datetime.utcnow()

    # Ensure all required fields are present
    if not movie.title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title is required."
        )
    if not movie.description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Description is required."
        )

    # Insert movie into database
    query = models.Movie.__table__.insert().values(
        title=movie.title,
        description=movie.description,
        release_date=release_date,
        user_id=current_user.id,
    )
    try:
        last_record_id = await database.execute(query)
        return {**movie.dict(), "id": last_record_id, "owner_id": current_user.id}

    except Exception as e:
        # Log the error and return a detailed message
        logger.error(f"Unexpected error while creating movie: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the movie: {str(e)}"
        )


@router.get("/movies/", response_model=List[schemas.Movie])
async def read_movies(skip: int = 0, limit: int = 10):
    query = select(
        models.Movie.id,
        models.Movie.title,
        models.Movie.description,
        models.Movie.release_date,
        models.Movie.user_id.label("owner_id")
    ).offset(skip).limit(limit)

    movies = await database.fetch_all(query)

    # Log fetched movies for debugging
    logger.info(f"Fetched movies: {movies}")

    return [
        schemas.Movie(
            id=movie["id"],
            title=movie["title"],
            description=movie["description"],
            release_date=movie["release_date"],
            owner_id=movie["owner_id"]
        )
        for movie in movies
    ]


@router.get("/movies/{movie_id}", response_model=schemas.Movie)
async def read_movie(movie_id: int):
    query = select(
        models.Movie.id,
        models.Movie.title,
        models.Movie.description,
        models.Movie.release_date,
        models.Movie.user_id.label("owner_id")
    ).where(models.Movie.id == movie_id)

    movie = await database.fetch_one(query)

    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    return schemas.Movie(
        id=movie["id"],
        title=movie["title"],
        description=movie["description"],
        release_date=movie["release_date"],
        owner_id=movie["owner_id"]
    )


@router.put("/movies/{movie_id}", response_model=schemas.Movie)
async def update_movie(movie_id: int, movie: schemas.MovieCreate,
                       current_user: models.User = Depends(get_current_user)):
    query = select(models.Movie).where(models.Movie.id == movie_id)
    db_movie = await database.fetch_one(query)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    if db_movie["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this movie")

    update_query = (
        update(models.Movie)
        .where(models.Movie.id == movie_id)
        .values(title=movie.title, description=movie.description)
    )
    await database.execute(update_query)
    return {**movie.dict(), "id": movie_id, "owner_id": current_user.id}


@router.delete("/movies/{movie_id}", response_model=dict)
async def delete_movie(movie_id: int, current_user: models.User = Depends(utils.get_current_user)):
    query = select(models.Movie).where(models.Movie.id == movie_id)
    db_movie = await database.fetch_one(query)

    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    if db_movie["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this movie")

    delete_query = delete(models.Movie).where(models.Movie.id == movie_id)
    await database.execute(delete_query)

    return {"message": "Movie deleted successfully"}
