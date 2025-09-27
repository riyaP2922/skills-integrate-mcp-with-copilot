"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# In-memory activity and member database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    # ...existing activities...
}

# New: In-memory member database
members = {
    # Example member
    "michael@mergington.edu": {
        "name": "Michael Smith",
        "email": "michael@mergington.edu",
        "roles": ["Chess Club:Coordinator"],
        "clubs": ["Chess Club"],
        "grade": "11"
    },
    # Add more members as needed
}

# New: List of possible roles
club_roles = ["Coordinator", "Head", "Executive", "Volunteer"]


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")



@app.get("/activities")
def get_activities():
    return activities

# New: Get all members
@app.get("/members")
def get_members():
    return members

# New: Add a member
@app.post("/members/add")
def add_member(name: str, email: str, grade: str):
    if email in members:
        raise HTTPException(status_code=400, detail="Member already exists")
    members[email] = {
        "name": name,
        "email": email,
        "roles": [],
        "clubs": [],
        "grade": grade
    }
    return {"message": f"Member {name} added."}

# New: Assign role to member in a club
@app.post("/members/{email}/assign-role")
def assign_role(email: str, club: str, role: str):
    if email not in members:
        raise HTTPException(status_code=404, detail="Member not found")
    if role not in club_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    if club not in activities:
        raise HTTPException(status_code=404, detail="Club not found")
    role_str = f"{club}:{role}"
    if role_str in members[email]["roles"]:
        raise HTTPException(status_code=400, detail="Role already assigned")
    members[email]["roles"].append(role_str)
    if club not in members[email]["clubs"]:
        members[email]["clubs"].append(club)
    return {"message": f"Assigned role {role} in {club} to {email}"}

# New: Remove member
@app.delete("/members/{email}/remove")
def remove_member(email: str):
    if email not in members:
        raise HTTPException(status_code=404, detail="Member not found")
    del members[email]
    return {"message": f"Member {email} removed."}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
