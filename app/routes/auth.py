from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlite3 import IntegrityError
import logging
from sqlalchemy import select
from app import models, schemas, utils
from app.database import database

router = APIRouter()

logger = logging.getLogger("uvicorn.error")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_user(username: str):
    query = select(models.User).where(models.User.username == username)
    return await database.fetch_one(query)


@router.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate):
    # Hash the password
    hashed_password = utils.get_password_hash(user.password)

    # Create the SQLAlchemy insert query
    query = models.User.__table__.insert().values(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    try:
        last_record_id = await database.execute(query)
        return {**user.dict(), "id": last_record_id}

    except IntegrityError as e:  # Change to the specific exception if necessary
        logger.error(f"IntegrityError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not utils.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = utils.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
