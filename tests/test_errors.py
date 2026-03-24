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


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity returns 404"""
    # Arrange: Use a non-existent activity name
    activity_name = "NonExistent Club"
    email = "test@example.com"
    
    # Act: Attempt to signup for non-existent activity
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check 404 error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_already_registered():
    """Test signing up when already registered returns 400"""
    # Arrange: First sign up for an activity
    activity_name = "Chess Club"
    email = "test@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act: Attempt to signup again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check 400 error response
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity returns 404"""
    # Arrange: Use a non-existent activity name
    activity_name = "NonExistent Club"
    email = "test@example.com"
    
    # Act: Attempt to unregister from non-existent activity
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert: Check 404 error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_not_registered():
    """Test unregistering when not registered returns 400"""
    # Arrange: Use an activity where the email is not registered
    activity_name = "Chess Club"
    email = "notregistered@example.com"
    
    # Act: Attempt to unregister without being registered
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert: Check 400 error response
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not registered for this activity"}