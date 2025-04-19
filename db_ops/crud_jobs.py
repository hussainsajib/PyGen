from db.models import Job, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def enqueue_job(session: AsyncSession, surah_number: int, surah_name: str, reciter: str,  scheduled_time=None):
    job = Job(
        surah_number=surah_number,
        surah_name=surah_name,
        reciter=reciter,
        scheduled_time=scheduled_time
    )
    session.add(job)
    await session.commit()
    return job

async def get_all_jobs(session: AsyncSession):
    result = await session.execute(select(Job).order_by(Job.id.asc()))
    return result.scalars().all()

async def update_job_progress(session: AsyncSession, job_id: int, progress: float):
    job = await session.get(Job, job_id)
    job.progress = progress
    await session.commit()
