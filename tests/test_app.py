"""
Unit tests for Mergington High School Activities API.
Tests use the AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Client is ready with test data
        Act: Make GET request to /activities
        Assert: Response contains all activities with required fields
        """
        # Arrange: (client fixture provides the test setup)
        
        # Act: GET request to retrieve all activities
        response = client.get("/activities")
        
        # Assert: Verify response status and structure
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Basketball Team" in activities
        
        # Verify activity structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_successful(self, client):
        """
        Test that a new student can successfully sign up for an activity.
        
        Arrange: Prepare a new email address and valid activity
        Act: POST to signup endpoint
        Assert: Student is added and response is successful
        """
        # Arrange: Set up test data
        new_email = "john.doe@mergington.edu"
        activity_name = "Chess Club"
        
        # Act: Send signup request
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert: Verify successful signup
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert new_email in result["message"]
        
        # Verify student was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_student_fails(self, client):
        """
        Test that a student already signed up gets a 400 error.
        
        Arrange: Use an email already in the activity
        Act: POST signup request with duplicate email
        Assert: Get 400 error response
        """
        # Arrange: Get current participants to find an existing student
        activities = client.get("/activities").json()
        existing_email = activities["Chess Club"]["participants"][0]
        activity_name = "Chess Club"
        
        # Act: Attempt to sign up with duplicate email
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]
    
    def test_signup_invalid_activity_fails(self, client):
        """
        Test that signing up for non-existent activity returns 404.
        
        Arrange: Use an activity that doesn't exist
        Act: POST signup request for invalid activity
        Assert: Get 404 error response
        """
        # Arrange: Set up request with invalid activity
        email = "test@mergington.edu"
        invalid_activity = "Nonexistent Activity"
        
        # Act: Attempt to sign up for invalid activity
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_existing_student_successful(self, client):
        """
        Test that an existing student can be unregistered from an activity.
        
        Arrange: Identify a student currently in an activity
        Act: Send DELETE request to unregister
        Assert: Student is removed and response is successful
        """
        # Arrange: Get an existing participant
        activities = client.get("/activities").json()
        activity_name = "Basketball Team"
        email_to_remove = activities[activity_name]["participants"][0]
        
        # Act: Send DELETE request to unregister
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email_to_remove}"
        )
        
        # Assert: Verify successful unregistration
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]
        assert email_to_remove in result["message"]
        
        # Verify student was actually removed
        activities_after = client.get("/activities").json()
        assert email_to_remove not in activities_after[activity_name]["participants"]
    
    def test_unregister_non_participant_fails(self, client):
        """
        Test that unregistering a student not in the activity returns 400.
        
        Arrange: Use an email not in the activity
        Act: Send DELETE request for non-participant
        Assert: Get 400 error response
        """
        # Arrange: Use an email not in this activity
        email = "notregistered@mergington.edu"
        activity_name = "Programming Class"
        
        # Act: Attempt to unregister non-participant
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"]
    
    def test_unregister_invalid_activity_fails(self, client):
        """
        Test that unregistering from non-existent activity returns 404.
        
        Arrange: Use an activity that doesn't exist
        Act: Send DELETE request for invalid activity
        Assert: Get 404 error response
        """
        # Arrange: Set up request with invalid activity
        email = "test@mergington.edu"
        invalid_activity = "Nonexistent Activity"
        
        # Act: Attempt to unregister from invalid activity
        response = client.delete(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Test that the root endpoint redirects to the static index.html.
        
        Arrange: Client is ready
        Act: Make GET request to root path
        Assert: Response is a redirect to /static/index.html
        """
        # Arrange: (client fixture provides setup)
        
        # Act: Make request to root path (follow_redirects=False to see redirect)
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect status and location
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
