import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Ensure backend directory is in the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.models.candidate import Candidate

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_api.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def db_session(anyio_backend):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    db = TestingSessionLocal()
    
    # Seed candidate with ID 1
    test_candidate = Candidate(
        id=1,
        name="John Doe",
        email="john@example.com",
        phone="+911234567890",
        applied_role="AI Engineer",
        experience_years=2,
        application_status="Applied"
    )
    db.add(test_candidate)
    await db.commit()
    await db.refresh(test_candidate)
    
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        if os.path.exists("./test_api.db"):
            try:
                os.remove("./test_api.db")
            except PermissionError:
                pass

@pytest.fixture(scope="module")
async def client(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

