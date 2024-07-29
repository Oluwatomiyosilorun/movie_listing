from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from .database import database
from .models import users
from .schemas import TokenData
from .auth import SECRET_KEY, ALGORITHM, oauth2_scheme


async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
