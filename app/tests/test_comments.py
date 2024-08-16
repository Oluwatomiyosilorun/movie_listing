import pytest
from httpx import AsyncClient
from ..main import app
from ..database import database

auth_token_value = None
movie_rating_id = None
comment_id = None


@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(scope="module")
async def get_auth_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/auth/token", data={"username": "testuser", "password": "testpassword"})
        assert login_response.status_code == 200, "Failed to login user"

        return login_response.json()["access_token"]


@pytest.fixture(scope="module")
async def stored_auth_token(get_auth_token):
    global auth_token_value
    auth_token_value = await get_auth_token


@pytest.fixture(scope="module")
async def movie_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token_value}"}
        movie_data = {"title": "Test Movie", "description": "A test movie"}
        response = await ac.post("/movies/", json=movie_data, headers=headers)
        assert response.status_code == 200, "Failed to create movie"

        return response.json()["id"]


@pytest.fixture(scope="module")
async def stored_movie_id(movie_id):
    global movie_rating_id
    movie_rating_id = await movie_id


@pytest.mark.asyncio
async def test_create_comment(stored_auth_token, stored_movie_id):
    await stored_auth_token
    await stored_movie_id
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token_value}"}
        comment_data = {"content": "This is a test comment"}
        response = await ac.post(f"/comments/{movie_rating_id}", json=comment_data, headers=headers)
        assert response.status_code == 200, "Failed to create comment"
        assert response.json()["content"] == comment_data["content"]

        global comment_id
        comment_id = response.json()["id"]


@pytest.mark.asyncio
async def test_read_comments(stored_movie_id):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/comments/{movie_rating_id}")
        assert response.status_code == 200, "Failed to read comments"
        assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_delete_comment(stored_auth_token, stored_movie_id):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token_value}"}

        delete_response = await ac.delete(f"/comments/{comment_id}", headers=headers)
        assert delete_response.status_code == 200, "Failed to delete comment"

