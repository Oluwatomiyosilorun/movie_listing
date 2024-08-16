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
def test_user_data():
    return {
        "username": "testuser001",
        "email": "testuser001@example.com",
        "password": "password"
    }


@pytest.mark.asyncio
async def test_register_user(test_user_data):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json=test_user_data)

        if response.status_code == 200:
            assert response.json()["username"] == test_user_data["username"]
            assert response.json()["email"] == test_user_data["email"]
        elif response.status_code == 409:
            assert response.json()["detail"] == "Username or email already registered"
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


@pytest.mark.asyncio
async def test_login_user(test_user_data):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/token",
                                 data={"username": test_user_data["username"], "password": test_user_data["password"]})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_invalid_credentials():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/token", data={"username": "nonexistent", "password": "wrongpassword"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect username or password"}
