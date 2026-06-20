def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Cipher" in response.json()["message"]

def test_get_candidate_profile_path_success(client):
    response = client.get("/candidate-profile/1")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_name"] == "John Doe"
    assert data["applied_role"] == "AI Engineer"
    assert data["experience"] == "2 years"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "+911234567890"
    assert data["status"] == "Applied"

def test_get_candidate_profile_query_id_success(client):
    response = client.get("/candidate-profile?candidate_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_name"] == "John Doe"

def test_get_candidate_profile_query_name_success(client):
    response = client.get("/candidate-profile?candidate_name=John Doe")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_name"] == "John Doe"

def test_get_candidate_profile_query_not_found(client):
    # An invalid ID should return 404 since it cannot auto-register without a name
    response = client.get("/candidate-profile?candidate_id=9999")
    assert response.status_code == 404

def test_screen_candidate_id_success(client):
    payload = {
        "candidate_id": 1,
        "experience_years": 2,
        "notice_period": "30 days",
        "expected_salary": "8 LPA",
        "interested": True,
        "introduction": "Hi, I am John Doe. I build LLMs."
    }
    response = client.post("/screen-candidate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["qualification_score"] == 95
    assert data["qualified"] is True
    assert data["status"] == "Screened - Qualified"

    # Verify status changed in candidate profile
    profile_response = client.get("/candidate-profile/1")
    assert profile_response.json()["status"] == "Screened - Qualified"

def test_screen_candidate_name_success_vapi(client):
    payload = {
        "candidate_name": "John Doe",
        "experience_years": "2",
        "notice_period": "30 days",
        "expected_salary": "8 LPA",
        "interested": True,
        "introduction": "Hello, I am John."
    }
    response = client.post("/screen-candidate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["qualification_score"] == 95
    assert data["qualified"] is True
    assert data["status"] == "Screened - Qualified"

def test_screen_candidate_name_unqualified_not_interested(client):
    payload = {
        "candidate_name": "John Doe",
        "experience_years": "5",
        "notice_period": "immediate",
        "expected_salary": "6 LPA",
        "interested": False,
        "introduction": "Hello"
    }
    response = client.post("/screen-candidate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["qualification_score"] == 0
    assert data["qualified"] is False
    assert data["status"] == "Screened - Unqualified"

def test_screen_candidate_not_found(client):
    # An invalid ID should return 404 since it cannot auto-register without a name
    payload = {
        "candidate_id": 9999,
        "experience_years": "2",
        "notice_period": "30 days",
        "expected_salary": "8 LPA",
        "interested": True
    }
    response = client.post("/screen-candidate", json=payload)
    assert response.status_code == 404

def test_check_availability_date_query(client):
    response = client.get("/check-availability?date=2026-06-25")
    assert response.status_code == 200
    data = response.json()
    assert "available_slots" in data
    assert len(data["available_slots"]) == 4

def test_schedule_interview_name_success_vapi(client):
    payload = {
        "candidate_name": "John Doe",
        "start_time": "2026-06-25T11:00:00Z"
    }
    response = client.post("/schedule-interview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["interview_id"] == "INT-1001"
    assert data["status"] == "Interview Scheduled"

    # Verify status changed in profile
    profile_response = client.get("/candidate-profile?candidate_name=John Doe")
    assert profile_response.json()["status"] == "Interview Scheduled"

def test_schedule_interview_not_found(client):
    # An invalid ID should return 404 since it cannot auto-register without a name
    payload = {
        "candidate_id": 9999,
        "start_time": "2026-06-25T11:00:00"
    }
    response = client.post("/schedule-interview", json=payload)
    assert response.status_code == 404

def test_get_candidate_profile_camelcase_query(client):
    response = client.get("/candidate-profile?candidateName=John Doe")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_name"] == "John Doe"

def test_get_candidate_profile_post_body(client):
    payload = {"candidateName": "John Doe"}
    response = client.post("/candidate-profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_name"] == "John Doe"

def test_screen_candidate_camelcase(client):
    payload = {
        "candidateName": "John Doe",
        "experienceYears": "2",
        "noticePeriod": "30 days",
        "expectedSalary": "8 LPA",
        "interested": True,
        "introduction": "Hi there"
    }
    response = client.post("/screen-candidate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["qualification_score"] == 95
    assert data["qualified"] is True

def test_schedule_interview_camelcase(client):
    payload = {
        "candidateName": "John Doe",
        "startTime": "2026-06-25T14:00:00"
    }
    response = client.post("/schedule-interview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_get_candidate_profile_auto_registration(client):
    # Query a name that doesn't exist in the database (e.g. 'Robert Downey')
    response = client.get("/candidate-profile?candidateName=Robert Downey")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_name"] == "Robert Downey"
    assert data["status"] == "Applied"
    assert data["applied_role"] == "AI Engineer"

    # Verify that we can query this candidate now
    verify_response = client.get("/candidate-profile?candidateName=Robert Downey")
    assert verify_response.status_code == 200
    assert verify_response.json()["candidate_name"] == "Robert Downey"


