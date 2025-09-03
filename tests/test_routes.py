import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_route_returns_200(client):
    rv = client.get("/")
    assert rv.status_code == 200

