"""
Pytest configuration and fixtures for FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import FastAPI, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient with a fresh FastAPI app instance.
    Each test gets an isolated app with its own in-memory activities database.
    """
    from src.app import app as original_app
    
    # Create a new app instance for this test
    test_app = FastAPI(title="Mergington High School API",
                       description="API for viewing and signing up for extracurricular activities")
    
    # Mount static files the same way as the original app
    from fastapi.staticfiles import StaticFiles
    import os
    from pathlib import Path
    
    test_app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent.parent,
              "src", "static")), name="static")
    
    # Copy the activity data for this test
    test_activities = {
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
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        }
    }
    
    # Add endpoints to the test app
    from fastapi import HTTPException
    from fastapi.responses import RedirectResponse
    
    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @test_app.get("/activities")
    def get_activities():
        return test_activities

    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = test_activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}

    @test_app.delete("/activities/{activity_name}/signup")
    def unregister_from_activity(activity_name: str, email: str):
        """Remove a student from an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = test_activities[activity_name]
        
        if email not in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student not signed up for this activity")
        
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}
    
    return TestClient(test_app)
