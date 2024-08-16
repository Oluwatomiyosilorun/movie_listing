# app/main.py
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.routes import auth, movies, comments, ratings
from app.database import database, create_tables

app = FastAPI(debug=True)


@app.on_event("startup")
async def startup():
    await database.connect()

    create_tables()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])


@app.get("/")
async def redirect():
    response = RedirectResponse(url='/docs')
    return response
