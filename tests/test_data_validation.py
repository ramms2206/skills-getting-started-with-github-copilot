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


def test_signup_with_empty_email():
    """Test signing up with an empty email string"""
    # Arrange: Set up test data with empty email
    activity_name = "Chess Club"
    email = ""
    
    # Act: Attempt to signup with empty email
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check that it succeeds (no validation currently)
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify empty email was added
    response_check = client.get("/activities")
    data = response_check.json()
    assert email in data[activity_name]["participants"]


def test_signup_with_special_characters_email():
    """Test signing up with email containing special characters"""
    # Arrange: Set up test data with special characters in email
    activity_name = "Programming Class"
    email = "test+special@example.com"
    
    # Act: Attempt to signup with special character email
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check that it succeeds
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify email was added
    response_check = client.get("/activities")
    data = response_check.json()
    assert email in data[activity_name]["participants"]


def test_signup_beyond_max_participants():
    """Test that signup allows going beyond max_participants (current behavior)"""
    # Arrange: Fill up an activity to max participants, then add one more
    activity_name = "Tennis Club"
    max_participants = activities[activity_name]["max_participants"]  # 10
    original_count = len(activities[activity_name]["participants"])  # 2
    
    # Add participants up to max
    for i in range(max_participants):
        email = f"participant{i}@example.com"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act: Add one more participant beyond max
    extra_email = "extra@example.com"
    response = client.post(f"/activities/{activity_name}/signup", params={"email": extra_email})
    
    # Assert: Check that it succeeds (no capacity check currently)
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {extra_email} for {activity_name}"}
    
    # Verify total participants exceeds max
    response_check = client.get("/activities")
    data = response_check.json()
    assert len(data[activity_name]["participants"]) == original_count + max_participants + 1


def test_multiple_signups_different_activities():
    """Test signing up for multiple different activities with same email"""
    # Arrange: Set up test data
    email = "multi@example.com"
    activity1 = "Chess Club"
    activity2 = "Programming Class"
    
    # Act: Signup for first activity
    response1 = client.post(f"/activities/{activity1}/signup", params={"email": email})
    # Signup for second activity
    response2 = client.post(f"/activities/{activity2}/signup", params={"email": email})
    
    # Assert: Both signups succeed
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() == {"message": f"Signed up {email} for {activity1}"}
    assert response2.json() == {"message": f"Signed up {email} for {activity2}"}
    
    # Verify email appears in both activities
    response_check = client.get("/activities")
    data = response_check.json()
    assert email in data[activity1]["participants"]
    assert email in data[activity2]["participants"]


def test_unregister_with_empty_email():
    """Test unregistering with an empty email string"""
    # Arrange: First sign up with empty email
    activity_name = "Art Studio"
    email = ""
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act: Attempt to unregister with empty email
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert: Check that it succeeds
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify empty email was removed
    response_check = client.get("/activities")
    data = response_check.json()
    assert email not in data[activity_name]["participants"]