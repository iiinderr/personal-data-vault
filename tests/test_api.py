from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """
    Basic test to check if API is running.
    """
    response = client.get("/")

    assert response.status_code == 200