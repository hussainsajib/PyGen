from db.models import Job, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

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
    
async def clear_completed_jobs(session):
    await session.execute(
        delete(Job).where(Job.status.in_([JobStatus.done]))
    )
    await session.commit()

async def delete_single_job(session: AsyncSession, job_id: int):
    job = await session.get(Job, job_id)
    if job:
        await session.delete(job)
        await session.commit()


async def retry_job(session: AsyncSession, job_id: int):
    job = await session.get(Job, job_id)
    if job:
        job.status = JobStatus.pending
        job.progress = 0.0
        job.retry_count = 0
        await session.commit()


async def enqueue_manual_upload_job(session: AsyncSession, video_filename: str, reciter_key: str, playlist_id: str, details_filename: str):
    import json
    data = {
        "video_filename": video_filename,
        "playlist_id": playlist_id,
        "details_filename": details_filename
    }
    job = Job(
        surah_number=0, # Special marker for manual upload
        surah_name=json.dumps(data),
        reciter=reciter_key
    )
    session.add(job)
    await session.commit()
    return job