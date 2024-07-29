from sqlalchemy import Table, Column, Integer, String, ForeignKey
from .database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("password", String),
)

movies = Table(
    "movies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("description", String),
    Column("user_id", Integer, ForeignKey("users.id")),
)

ratings = Table(
    "ratings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("rating", Integer),
)

comments = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("parent_id", Integer, ForeignKey("comments.id"), nullable=True),
    Column("text", String),
)
