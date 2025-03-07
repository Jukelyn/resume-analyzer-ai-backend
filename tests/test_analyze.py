import pytest
from app import app

@pytest.fixture
def client():
    """Fixture to create a test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_analyze_success(client):
    """Test if the /analyze endpoint returns a valid response."""
    response = client.post("/analyze", json={"text": "Analyze this text."})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert "analysis" in json_data
    assert isinstance(json_data["analysis"], str)  # Ensure response is a string

def test_analyze_missing_text(client):
    """Test if the /analyze endpoint handles missing text correctly."""
    response = client.post("/analyze", json={})  # No text field
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {"error": "No text provided"}
