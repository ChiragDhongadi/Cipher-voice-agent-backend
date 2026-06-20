import os
import sys
import asyncio

# Ensure backend directory is in the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.candidate import Candidate
from sqlalchemy import select, func

async def seed_db():
    async with SessionLocal() as db:
        try:
            stmt = select(func.count()).select_from(Candidate)
            result = await db.execute(stmt)
            count = result.scalar()
            if count > 0:
                print("Database already contains candidates. Seeding skipped.")
                return

            candidates = [
                Candidate(
                    name="John Doe",
                    email="john@example.com",
                    phone="+911234567890",
                    applied_role="AI Engineer",
                    experience_years=2,
                    application_status="Applied"
                ),
                Candidate(
                    name="Jane Smith",
                    email="jane@example.com",
                    phone="+919876543210",
                    applied_role="Fullstack Engineer",
                    experience_years=5,
                    application_status="Applied"
                ),
                Candidate(
                    name="Alice Johnson",
                    email="alice@example.com",
                    phone="+915555555555",
                    applied_role="Product Manager",
                    experience_years=1,
                    application_status="Applied"
                )
            ]

            db.add_all(candidates)
            await db.commit()
            print("Successfully seeded candidate data!")
        except Exception as e:
            print(f"Error during seeding: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_db())

