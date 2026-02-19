import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Test signing up for an activity
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@mergington.edu for Chess Club" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student is already signed up" in data["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Soccer%20Team/signup?email=unregister@mergington.edu")
    # Then unregister
    response = client.post("/activities/Soccer%20Team/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@mergington.edu from Soccer Team" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@mergington.edu" not in data["Soccer Team"]["participants"]

def test_unregister_not_registered():
    response = client.post("/activities/Soccer%20Team/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student is not registered" in data["detail"]

def test_unregister_activity_not_found():
    response = client.post("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]