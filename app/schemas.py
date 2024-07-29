from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class MovieCreate(BaseModel):
    title: str
    description: str


class Movie(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

    class Config:
        orm_mode = True


class RatingCreate(BaseModel):
    movie_id: int
    rating: int


class Rating(BaseModel):
    id: int
    movie_id: int
    user_id: int
    rating: int

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    movie_id: int
    parent_id: int | None
    text: str


class Comment(BaseModel):
    id: int
    movie_id: int
    user_id: int
    parent_id: int | None
    text: str

    class Config:
        orm_mode = True
