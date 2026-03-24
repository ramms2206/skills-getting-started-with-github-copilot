import pytest
import copy
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state after each test"""
    # Arrange: Save original activities data
    original_activities = copy.deepcopy(activities)
    
    yield
    
    # Cleanup: Restore original activities data
    activities.clear()
    activities.update(original_activities)


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange: No special setup needed
    
    # Act: Make GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check response status and data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Should have 9 activities
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Arrange: Set up test data
    activity_name = "Chess Club"
    email = "test@example.com"
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check response and that participant was added
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify participant was added to activity
    response_check = client.get("/activities")
    data = response_check.json()
    assert email in data[activity_name]["participants"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # Arrange: First sign up for an activity
    activity_name = "Programming Class"
    email = "test@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert: Check response and that participant was removed
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify participant was removed from activity
    response_check = client.get("/activities")
    data = response_check.json()
    assert email not in data[activity_name]["participants"]


def test_root_redirect():
    """Test root endpoint redirects to static index"""
    # Arrange: No special setup needed
    
    # Act: Make GET request to root
    response = client.get("/", follow_redirects=False)
    
    # Assert: Check redirect response
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"