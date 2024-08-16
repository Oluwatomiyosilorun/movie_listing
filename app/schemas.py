from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None


class MovieCreate(MovieBase):
    release_date: Optional[datetime] = None


class Movie(MovieBase):
    id: int
    owner_id: int
    release_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class RatingBase(BaseModel):
    rating: float


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    user_id: int
    movie_id: int

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str
    parent_comment_id: Optional[int] = None


class CommentCreate(CommentBase):
    parent_comment_id: Optional[int] = None


class Comment(CommentBase):
    id: int
    user_id: int
    movie_id: int
    parent_comment_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True
