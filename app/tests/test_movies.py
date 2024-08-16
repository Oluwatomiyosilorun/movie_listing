import pytest
from httpx import AsyncClient
from ..main import app
from ..database import database


@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(scope="module")
async def auth_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password"}
        register_response = await ac.post("/auth/register", json=user_data)
        assert register_response.status_code in [200, 409], f"Failed to register user: {register_response.text}"

        login_response = await ac.post("/auth/token", data={"username": "testuser", "password": "password"})
        assert login_response.status_code == 200, f"Failed to login user: {login_response.text}"

        return login_response.json()["access_token"]


@pytest.fixture(scope="function")
async def test_create_movie(auth_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        movie_data = {"title": "Test Movie", "description": "A test movie"}
        response = await ac.post("/movies/", json=movie_data, headers=headers)
        assert response.status_code == 200, f"Failed to create movie: {response.text}"
        return response.json()["id"]


@pytest.mark.asyncio
async def test_read_movies(auth_token, test_create_movie):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/movies/")
        assert response.status_code == 200, f"Failed to read movies: {response.text}"
        assert len(response.json()) > 0, "No movies found"


@pytest.mark.asyncio
async def test_read_movie(auth_token, test_create_movie):
    movie_id = await test_create_movie
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/movies/{movie_id}")
        assert response.status_code == 200, f"Failed to read movie: {response.text}"
        assert response.json()["id"] == movie_id


@pytest.mark.asyncio
async def test_update_movie(auth_token, test_create_movie):
    movie_id = await test_create_movie
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        updated_movie_data = {"title": "Updated Movie Title", "description": "Updated movie description"}
        response = await ac.put(f"/movies/{movie_id}", json=updated_movie_data, headers=headers)
        assert response.status_code == 200, f"Failed to update movie: {response.text}"
        assert response.json()["title"] == updated_movie_data["title"]


@pytest.mark.asyncio
async def test_delete_movie(auth_token, test_create_movie):
    movie_id = await test_create_movie
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await ac.delete(f"/movies/{movie_id}", headers=headers)
        assert response.status_code == 200, f"Failed to delete movie: {response.text}"

        # Try to get the deleted movie, expecting a 404
        get_response = await ac.get(f"/movies/{movie_id}")
        assert get_response.status_code == 404, f"Deleted movie still accessible: {get_response.text}"
