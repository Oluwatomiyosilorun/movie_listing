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
        # Register and login a user to get an auth token
        user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
        register_response = await ac.post("/auth/register", json=user_data)
        assert register_response.status_code in [200, 409], "Failed to register user"

        login_response = await ac.post("/auth/token", data={"username": "testuser", "password": "testpassword"})
        assert login_response.status_code == 200, f"Failed to login user: {login_response.text}"

        return login_response.json()["access_token"]


@pytest.fixture(scope="module")
async def movie_id(auth_token):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        movie_data = {"title": "Test Movie", "description": "A test movie"}
        response = await ac.post("/movies/", json=movie_data, headers=headers)
        assert response.status_code == 200, f"Failed to create movie: {response.text}"

        return response.json()["id"]


@pytest.mark.asyncio
async def test_create_rating(auth_token, movie_id):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {await auth_token}"}
        rating_data = {"rating": 4.5}
        response = await ac.post(f"/movies/{await movie_id}/ratings/", json=rating_data, headers=headers)
        assert response.status_code == 200, f"Failed to create rating: {response.text}"
        assert response.json()["rating"] == rating_data["rating"]


@pytest.mark.asyncio
async def test_read_ratings(movie_id):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/movies/{await movie_id}/ratings/")
        assert response.status_code == 200, f"Failed to read ratings: {response.text}"
        assert len(response.json()) > 0, "No ratings found"
