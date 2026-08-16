import asyncio
import uuid
import logging
from sqlalchemy import select, delete, text
from app.database.session import AsyncSessionLocal, engine
from app.core.base_class import Base
from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.action import ActionProposal
from app.models.enums import JobStatus

logger = logging.getLogger(__name__)

# Hardcoded realistic demo job
DEMO_JOB = {
    "title": "Senior Backend Engineer (AI Platform)",
    "description": (
        "We are looking for a Senior Backend Engineer to build robust AI platforms. "
        "You must have strong experience with Python, FastAPI, and SQL databases. "
        "Experience with cloud deployments (AWS or GCP) and machine learning pipelines is a huge plus."
    ),
    "department": "Engineering",
    "location": "San Francisco, CA (Hybrid)",
    "skills": ["Python", "FastAPI", "SQL", "Machine Learning", "AWS", "Backend"],
    "status": JobStatus.ACTIVE,
    "is_demo": True
}

# Hardcoded realistic demo candidates
DEMO_CANDIDATES = [
    {
        "name": "Alice Chen",
        "email": "alice.chen@example.com",
        "phone": "+1-555-0101",
        "skills": ["Python", "FastAPI", "SQL", "AWS", "PostgreSQL", "Docker", "Machine Learning"],
        "experience": [
            {"title": "Senior Backend Engineer", "company": "DataCorp", "years": 4, "description": "Built high-performance APIs using FastAPI and Python. Scaled Postgres databases on AWS. Integrated ML models."}
        ],
        "education": "MS Computer Science, Stanford University",
        "is_demo": True
    },
    {
        "name": "Bob Smith",
        "email": "bob.smith@example.com",
        "phone": "+1-555-0202",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express", "CSS", "HTML"],
        "experience": [
            {"title": "Frontend Developer", "company": "WebTech", "years": 3, "description": "Developed SPA using React and Node.js. Built beautiful user interfaces."}
        ],
        "education": "BS Computer Science, State University",
        "is_demo": True
    },
    {
        "name": "Charlie Davis",
        "email": "charlie.davis@example.com",
        "phone": "+1-555-0303",
        "skills": ["Python", "Django", "SQL", "GCP", "Kubernetes", "Redis", "Machine Learning"],
        "experience": [
            {"title": "Backend Developer", "company": "CloudSys", "years": 5, "description": "Designed microservices architecture using Django and Python. Deployed on GCP using Kubernetes."}
        ],
        "education": "BS Software Engineering",
        "is_demo": True
    },
    {
        "name": "Diana Prince",
        "email": "diana.prince@example.com",
        "phone": "+1-555-0404",
        "skills": ["Java", "Spring Boot", "Oracle", "AWS", "Kafka"],
        "experience": [
            {"title": "Enterprise Java Developer", "company": "MegaBank", "years": 7, "description": "Maintained legacy banking applications in Java Spring Boot. High reliability systems."}
        ],
        "education": "BS Information Systems",
        "is_demo": True
    }
]


async def seed_demo_data():
    # Ensure all tables exist in database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        logger.info("Clearing existing demo data...")
        
        # Clear matches and action proposals tied to demo jobs first
        jobs_res = await db.execute(select(Job.id).where(Job.title == DEMO_JOB["title"]))
        demo_job_ids = jobs_res.scalars().all()
        if demo_job_ids:
            await db.execute(delete(Match).where(Match.job_id.in_(demo_job_ids)))
            await db.execute(delete(ActionProposal).where(ActionProposal.job_id.in_(demo_job_ids)))
        
        # Now delete the demo job
        await db.execute(delete(Job).where(Job.title == DEMO_JOB["title"]))
        
        # Delete demo candidates
        await db.execute(delete(Candidate).where(Candidate.email.like("%@example.com")))
        await db.commit()
        
        logger.info("Seeding Demo Job...")
        job = Job(
            id=uuid.uuid4(),
            title=DEMO_JOB["title"],
            description=DEMO_JOB["description"],
            department=DEMO_JOB["department"],
            location=DEMO_JOB["location"],
            skills=DEMO_JOB["skills"],
            status=DEMO_JOB["status"]
        )
        db.add(job)
        
        logger.info("Seeding Demo Candidates...")
        for c in DEMO_CANDIDATES:
            cand = Candidate(
                id=uuid.uuid4(),
                profile_jsonb={
                    "name": c["name"],
                    "email": c["email"],
                    "phone": c["phone"],
                    "skills": c["skills"],
                    "experience": c["experience"],
                    "education": c["education"]
                }
            )
            cand.email = c["email"]
            cand.name = c["name"]
            db.add(cand)
            
        await db.commit()
        logger.info(f"Demo Job ID: {job.id}")
        logger.info("Demo data seeded successfully. Run the pipeline on this job to see deterministic ranking.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_demo_data())
