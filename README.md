# Cipher Technical Interview Agent Backend

Cipher is a conversational AI Technical Interviewer that calls candidates, greets them, collects their self-introduction, asks role-specific technical Q&A, and evaluates them on standard screening criteria (experience years, notice period, and expected salary) before booking an interview slot if they pass the qualification threshold.

This FastAPI backend provides endpoints for retrieving candidate profile details, evaluating screening responses, checking interview slot availability, and scheduling interviews.

---

## Tech Stack

* Python 3.14+
* FastAPI
* PostgreSQL (with SQLite fallback for local testing)
* SQLAlchemy ORM
* Pydantic (data validation and schemas)
* Alembic (database migrations)
* Uvicorn (ASGI server)
* Environment variables using `python-dotenv`

---

## Project Structure

```
backend/
├── alembic/              # Database migration scripts
├── app/
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic validation schemas
│   ├── routers/          # FastAPI routers (API endpoints)
│   ├── services/         # Business logic layer
│   ├── config.py         # Application configuration
│   ├── database.py       # DB engine, session and dependency configuration
│   ├── main.py           # FastAPI entrypoint
│   └── seed.py           # Database seeder script
├── tests/                # Automated API test suite
├── dashboard.py          # Streamlit visual testing portal
├── .env.example          # Template for environment variables
├── .env                  # Local environment variables
└── README.md             # Documentation
```

---

## Database Models

### 1. Candidate
* `id`: Unique identifier (autoincrement)
* `name`: Candidate's full name
* `email`: Candidate's unique email address
* `phone`: Candidate's phone number
* `applied_role`: Role they applied for (e.g., `"AI Engineer"`)
* `experience_years`: Candidate's experience from application
* `application_status`: Current application status (defaults to `"Applied"`)
* `created_at`: Creation timestamp

### 2. InterviewSession
* `id`: Unique identifier
* `candidate_id`: Foreign key referencing Candidate
* `introduction`: Text transcript of the candidate's self-introduction
* `experience_years`: Total years of experience confirmed during the call
* `notice_period`: Notice period (e.g., `"30 days"`)
* `expected_salary`: Expected salary (e.g., `"8 LPA"`)
* `interested`: Boolean indicating candidate interest
* `screening_score`: Calculated qualification score (0 - 100)
* `qualified`: Boolean indicating if they qualified (score >= 70)
* `created_at`: Creation timestamp

### 3. Interview
* `id`: Unique identifier
* `candidate_id`: Foreign key referencing Candidate
* `interview_date`: Date of the interview
* `interview_time`: Time of the interview
* `status`: Current status (defaults to `"Scheduled"`)
* `created_at`: Creation timestamp

---

## Business & Scoring Logic

The screening score is calculated out of 100 points based on the following algorithm:
1. **Base Score**: 20 points
2. **Experience**: 15 points per year (capped at 45 points for 3+ years)
3. **Notice Period**:
   * Immediate / <= 15 days: 30 points
   * <= 30 days: 20 points
   * <= 60 days: 10 points
   * > 60 days: 0 points
4. **Expected Salary**:
   * <= 8 LPA: 25 points
   * 9 - 12 LPA: 20 points
   * 13 - 15 LPA: 10 points
   * > 15 LPA: 5 points
   * Fallback / Non-parsable: 15 points
5. **Interest Check**:
   * Candidate **must** be interested. If `interested` is `False`, the total score is overridden to `0` and `qualified` is marked `False`.
6. **Qualification**:
   * Candidate is marked `qualified=True` if the final score is **>= 70**.
   * If qualified, their status updates to `"Screened - Qualified"`. Otherwise, it updates to `"Screened - Unqualified"`.

---

## Getting Started

### 1. Set Up Virtual Environment & Environment Variables
From the project root:
```bash
# Create and activate virtual environment (if not already done)
python -m venv .venv
.venv\Scripts\activate

# Move to backend directory
cd backend

# Create .env from template
copy .env.example .env
```

### 2. Apply Migrations
Alembic is configured to run migrations against whichever database URL is specified in your `.env` file (defaults to sqlite `cipher.db` locally).
```bash
alembic upgrade head
```

### 3. Seed Sample Candidate Data
Insert test profiles into the database:
```bash
python app/seed.py
```

### 4. Run the Server
Launch the FastAPI development server:
```bash
uvicorn app.main:app --reload
```
The API documentation will be available at:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run Automated Tests
You can run the full automated test suite using:
```bash
pytest tests/
```

### 6. Run the Interactive Testing Dashboard
To launch the interactive testing dashboard:
```bash
streamlit run dashboard.py
```
This opens the dashboard in your browser at [http://localhost:8501](http://localhost:8501). You can test all integration endpoints against the live FastAPI server while inspecting database records in real-time.

---

## API & Vapi Integration (Sample cURL Requests)

### 1. Get Candidate Profile (`get_candidate_profile`)
**Endpoint**: `GET /candidate-profile`

* **cURL Request (Query Parameter)**:
```bash
curl -X 'GET' \
  'http://localhost:8000/candidate-profile?candidate_name=John%20Doe' \
  -H 'accept: application/json'
```

* **Sample Response**:
```json
{
  "candidate_name": "John Doe",
  "applied_role": "AI Engineer",
  "experience": "2 years",
  "email": "john@example.com",
  "phone": "+911234567890",
  "status": "Applied"
}
```

---

### 2. Screen Candidate (`screen_candidate`)
**Endpoint**: `POST /screen-candidate`

* **cURL Request**:
```bash
curl -X 'POST' \
  'http://localhost:8000/screen-candidate' \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json' \
  -d '{
  "candidate_name": "John Doe",
  "experience_years": "2",
  "notice_period": "30 days",
  "expected_salary": "8 LPA",
  "interested": true,
  "introduction": "Hello, I am John Doe. I build LLMs."
}'
```

* **Sample Response**:
```json
{
  "qualification_score": 95,
  "qualified": true,
  "status": "Screened - Qualified"
}
```

---

### 3. Check Interview Availability (`check_availability`)
**Endpoint**: `GET /check-availability`

* **cURL Request**:
```bash
curl -X 'GET' \
  'http://localhost:8000/check-availability?date=2026-06-25' \
  -H 'accept: application/json'
```

* **Sample Response**:
```json
{
  "available_slots": [
    "10:00 AM",
    "11:00 AM",
    "02:00 PM",
    "04:00 PM"
  ]
}
```

---

### 4. Schedule Interview (`schedule_interview`)
**Endpoint**: `POST /schedule-interview`

* **cURL Request**:
```bash
curl -X 'POST' \
  'http://localhost:8000/schedule-interview' \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json' \
  -d '{
  "candidate_name": "John Doe",
  "start_time": "2026-06-25T11:00:00Z"
}'
```

* **Sample Response**:
```json
{
  "success": true,
  "interview_id": "INT-1001",
  "status": "Interview Scheduled"
}
```
