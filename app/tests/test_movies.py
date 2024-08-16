import pytest
from httpx import AsyncClient
from ..main import app
from ..database import database

auth_token_value = None


@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(scope="module", autouse=True)
async def get_auth_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/auth/token", data={"username": "tester", "password": "password"})
        assert login_response.status_code == 200, f"Failed to login user: {login_response.text}"

        return login_response.json()["access_token"]


@pytest.fixture(scope="module")
async def stored_auth_token(get_auth_token):
    global auth_token_value
    auth_token_value = await get_auth_token


@pytest.fixture(scope="function")
async def test_create_movie(stored_auth_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token_value}"}
        movie_data = {"title": "Mount Zion", "description": "A test movie"}
        response = await ac.post("/movies/", json=movie_data, headers=headers)
        assert response.status_code == 200, f"Failed to create movie: {response.text}"
        return response.json()["id"]


@pytest.mark.asyncio
async def test_read_movies(test_create_movie):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/movies/")
        assert response.status_code == 200, f"Failed to read movies: {response.text}"
        assert len(response.json()) > 0, "No movies found"


@pytest.mark.asyncio
async def test_read_movie(stored_auth_token, test_create_movie):
    await stored_auth_token
    movie_id = await test_create_movie
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/movies/{movie_id}")
        assert response.status_code == 200, f"Failed to read movie: {response.text}"
        assert response.json()["id"] == movie_id


@pytest.mark.asyncio
async def test_update_movie(test_create_movie):
    movie_id = await test_create_movie
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token_value}"}
        updated_movie_data = {"title": "Updated Movie Title", "description": "Updated movie description"}
        response = await ac.put(f"/movies/{movie_id}", json=updated_movie_data, headers=headers)
        assert response.status_code == 200, f"Failed to update movie: {response.text}"
        assert response.json()["title"] == updated_movie_data["title"]

@pytest.mark.asyncio
async def test_delete_movie(test_create_movie):
    movie_id = await test_create_movie
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token_value}"}
        response = await ac.delete(f"/movies/{movie_id}", headers=headers)
        assert response.status_code == 200, f"Failed to delete movie: {response.text}"

        # Try to get the deleted movie, expecting a 404
        get_response = await ac.get(f"/movies/{movie_id}")
        assert get_response.status_code == 404, f"Deleted movie still accessible: {get_response.text}"
