import pytest
from httpx import AsyncClient
from .. import models
from ..main import app


@pytest.mark.asyncio
async def test_create_comment(monkeypatch):
    async def mock_get_current_user():
        return models.User(id=1, email="tester@example.com", hashed_password="password")

    async def mock_execute(query):
        return 1

    monkeypatch.setattr("app.routes.comments.get_current_user", mock_get_current_user)
    monkeypatch.setattr("app.database.database.execute", mock_execute)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/comments/movies/1/comments/", json={
            "content": "Great movie!",
            "parent_comment_id": None
        })

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "content": "Great movie!",
        "movie_id": 1,
        "user_id": 1,
        "parent_comment_id": None,
        "created_at": response.json()["created_at"]
    }


@pytest.mark.asyncio
async def test_read_comments(monkeypatch):
    mock_comments = [
        {
            "id": 1,
            "content": "Great movie!",
            "movie_id": 1,
            "user_id": 1,
            "parent_comment_id": None,
            "created_at": "2024-08-16T12:00:00"
        }
    ]

    async def mock_fetch_all(query):
        return mock_comments

    monkeypatch.setattr("app.database.database.fetch_all", mock_fetch_all)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/comments/movies/1/comments/")

    assert response.status_code == 200
    assert response.json() == mock_comments


@pytest.mark.asyncio
async def test_delete_comment(monkeypatch):
    async def mock_get_current_user():
        return models.User(id=1, email="tester@example.com", hashed_password="password")

    async def mock_fetch_one(query):
        return {"id": 1, "user_id": 1}

    async def mock_execute(query):
        return 1

    monkeypatch.setattr("app.routes.comments.get_current_user", mock_get_current_user)
    monkeypatch.setattr("app.database.database.fetch_one", mock_fetch_one)
    monkeypatch.setattr("app.database.database.execute", mock_execute)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/comments/comments/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Comment deleted successfully"}

    # Test when comment does not exist
    async def mock_fetch_one_none(query):
        return None

    monkeypatch.setattr("app.database.database.fetch_one", mock_fetch_one_none)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/comments/comments/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Comment not found"}

    async def mock_fetch_one_forbidden(query):
        return {"id": 1, "user_id": 2}

    monkeypatch.setattr("app.database.database.fetch_one", mock_fetch_one_forbidden)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/comments/comments/1")

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to delete this comment"}
