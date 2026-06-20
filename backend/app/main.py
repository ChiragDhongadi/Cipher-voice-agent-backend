from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import candidates, screening, availability, interviews
from app.database import Base, engine, DATABASE_URL

app = FastAPI(
    title="Cipher Interview Agent Backend",
    description="Backend API for Cipher, the conversational AI Technical Interviewer.",
    version="1.0.0"
)

# Auto-create tables on startup only if SQLite is used to simplify testing
@app.on_event("startup")
async def startup_event():
    from app.models.candidate import Candidate
    from app.models.interview_session import InterviewSession
    from app.models.interview import Interview
    if "sqlite" in DATABASE_URL:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error_type": exc.__class__.__name__,
            "message": str(exc)
        }
    )

app.include_router(candidates.router, tags=["Candidates"])
app.include_router(screening.router, tags=["Screening"])
app.include_router(availability.router, tags=["Availability"])
app.include_router(interviews.router, tags=["Interviews"])

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to Cipher Technical Interview Agent API. Visit /docs for Swagger documentation."
    }
