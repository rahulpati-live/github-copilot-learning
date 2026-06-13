"""
Pytest tests for the FastAPI backend application.

Tests use Arrange-Act-Assert style to validate activity retrieval,
signup, duplicate signup handling, and participant removal.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Team practice and pick-up games for basketball enthusiasts",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Swimming Team": {
        "description": "Swim training, drills, and competitive meets",
        "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media art projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, script reading, and theater production practice",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["harper@mergington.edu", "benjamin@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Build robots and learn engineering principles through hands-on projects",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Prepare for debate competitions and improve public speaking skills",
        "schedule": "Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "jackson@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before every test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Create a FastAPI TestClient for each test."""
    return TestClient(app)


class TestGetActivities:
    """Tests for retrieving activities."""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity_names = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Club",
            "Swimming Team",
            "Art Club",
            "Drama Club",
            "Robotics Club",
            "Debate Team",
        }

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert set(activities_data.keys()) == expected_activity_names
        for details in activities_data.values():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignup:
    """Tests for signing up to activities."""

    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {new_student_email} for {activity_name}"
        }
        assert new_student_email in activities[activity_name]["participants"]

    def test_duplicate_signup_raises_error(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_student_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student_email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


class TestDeleteParticipant:
    """Tests for removing participants from activities."""

    def test_delete_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email_to_remove} from {activity_name}"
        }
        assert email_to_remove not in activities[activity_name]["participants"]

    def test_delete_participant_not_found(self, client):
        # Arrange
        activity_name = "Chess Club"
        missing_email = "missing@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": missing_email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
