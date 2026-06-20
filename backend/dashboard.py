import streamlit as st
import datetime as dt
import requests
import os
import sys
import pandas as pd

# Add app folder path to allow direct DB queries for visualization
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.candidate import Candidate
from app.models.interview_session import InterviewSession as DBInterviewSession
from app.models.interview import Interview as DBInterview

# Create a local synchronous engine specifically for the Streamlit dashboard inspector
sync_engine = create_engine(
    "sqlite:///./cipher.db", connect_args={"check_same_thread": False}
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

st.title("Cipher Technical Interview Agent - Testing Portal")
base_url = st.text_input("Backend URL", "http://localhost:8000").rstrip("/")

# Helper function to query local DB directly for visual verification
def get_db_records():
    db = SyncSessionLocal()

    try:
        candidates = db.query(Candidate).all()
        sessions = db.query(DBInterviewSession).all()
        interviews = db.query(DBInterview).all()
        
        c_df = pd.DataFrame([{
            "id": c.id, "name": c.name, "email": c.email, "phone": c.phone, 
            "applied_role": c.applied_role, "experience_years": c.experience_years, 
            "application_status": c.application_status
        } for c in candidates])
        
        s_df = pd.DataFrame([{
            "id": s.id, 
            "candidate_id": s.candidate_id, 
            "introduction": s.introduction[:40] + "..." if s.introduction else "",
            "experience_years": s.experience_years,
            "notice_period": s.notice_period,
            "expected_salary": s.expected_salary, 
            "score": s.screening_score, 
            "qualified": s.qualified
        } for s in sessions])
        
        i_df = pd.DataFrame([{
            "id": i.id, "candidate_id": i.candidate_id, "interview_date": str(i.interview_date),
            "interview_time": str(i.interview_time), "status": i.status
        } for i in interviews])
        
        return c_df, s_df, i_df
    finally:
        db.close()

# 1. GET PROFILE SECTION
st.subheader("Get Candidate Profile")
profile_name = st.text_input("Candidate name to check")

if st.button("Check Profile"):
    try:
        params = {"candidate_name": profile_name.strip()}
        resp = requests.get(f"{base_url}/candidate-profile", params=params, timeout=10)
        resp.raise_for_status()
        st.json(resp.json())
    except requests.RequestException as exc:
        st.error(f"Could not load candidate profile: {exc}")

st.divider()

# 2. SCREEN CANDIDATE SECTION
st.subheader("Screen Candidate")
screen_name = st.text_input("Candidate name to screen")
introduction = st.text_area("Candidate Introduction")
experience_years = st.number_input("Experience (years)", min_value=0, max_value=50, value=2)
notice_period = st.text_input("Notice period", "30 days")
expected_salary = st.text_input("Expected salary", "8 LPA")
interested = st.checkbox("Interested", value=True)

if st.button("Screen Candidate"):
    payload = {
        "candidate_name": screen_name.strip(),
        "experience_years": str(experience_years),
        "notice_period": notice_period.strip(),
        "expected_salary": expected_salary.strip(),
        "interested": interested,
        "introduction": introduction.strip()
    }
    try:
        resp = requests.post(f"{base_url}/screen-candidate", json=payload, timeout=10)
        resp.raise_for_status()
        st.success("Screening Logged Successfully")
        st.json(resp.json())
    except requests.RequestException as exc:
        st.error(f"Screening failed: {exc}")


st.divider()

# 3. SCHEDULE INTERVIEW SECTION
st.subheader("Schedule Interview")
schedule_name = st.text_input("Candidate name to schedule")
interview_date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1))

# Dynamically fetch available slots
available_slots = ["10:00 AM", "11:00 AM", "02:00 PM", "04:00 PM"]
try:
    avail_resp = requests.get(f"{base_url}/check-availability", timeout=5)
    if avail_resp.status_code == 200:
        available_slots = avail_resp.json().get("available_slots", available_slots)
except Exception:
    pass

selected_time = st.selectbox("Time slot", available_slots)

if st.button("Schedule"):
    # Convert slot time e.g., "11:00 AM" to 24h format "11:00:00"
    try:
        time_obj = dt.datetime.strptime(selected_time, "%I:%M %p")
        time_24h = time_obj.strftime("%H:%M:%S")
    except ValueError:
        time_24h = "11:00:00"
        
    start_time_iso = f"{interview_date.isoformat()}T{time_24h}"
    
    payload = {
        "candidate_name": schedule_name.strip(),
        "start_time": start_time_iso
    }
    try:
        resp = requests.post(f"{base_url}/schedule-interview", json=payload, timeout=10)
        resp.raise_for_status()
        st.success("Interview Scheduled")
        st.json(resp.json())
    except requests.RequestException as exc:
        st.error(f"Schedule failed: {exc}")

st.divider()

# 4. DATABASE RECORDS VISUALIZER
st.subheader("Live Database Inspector")
if st.button("Refresh Database Records"):
    st.rerun()

try:
    c_df, s_df, i_df = get_db_records()
    
    st.markdown("### Candidates")
    if not c_df.empty:
        st.dataframe(c_df, use_container_width=True, hide_index=True)
    else:
        st.info("No candidates registered.")
        
    st.markdown("### Interview Sessions")
    if not s_df.empty:
        st.dataframe(s_df, use_container_width=True, hide_index=True)
    else:
        st.info("No interview screening sessions recorded.")
        
    st.markdown("### Interviews")
    if not i_df.empty:
        st.dataframe(i_df, use_container_width=True, hide_index=True)
    else:
        st.info("No scheduled interviews found.")
        
except Exception as db_exc:
    st.error(f"Could not load database visualizer: {db_exc}")
