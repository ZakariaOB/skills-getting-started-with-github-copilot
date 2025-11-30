"""Tests for FastAPI activity endpoints."""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) >= 2
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activities include participant lists."""
        response = client.get("/activities")
        data = response.json()
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include all required fields."""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_succeeds(self, client, reset_activities):
        """Test signing up a new participant successfully."""
        response = client.post(
            "/activities/Chess Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newemail@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup adds participant to the activity's participants list."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
    
    def test_signup_duplicate_email_fails(self, client, reset_activities):
        """Test that signing up with duplicate email fails."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for non-existent activity fails."""
        response = client.post(
            "/activities/NonExistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities."""
        email = "student@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_participant_succeeds(self, client, reset_activities):
        """Test unregistering an existing participant."""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from the list."""
        # Unregister participant
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering non-existent participant fails."""
        response = client.post(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from non-existent activity fails."""
        response = client.post(
            "/activities/NonExistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test full lifecycle: signup then unregister."""
        email = "student@mergington.edu"
        
        # Sign up
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Verify added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        
        # Unregister
        response2 = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]


class TestRoot:
    """Tests for root endpoint."""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
