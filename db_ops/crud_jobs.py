from db.models import Job, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

async def enqueue_job(
    session: AsyncSession, 
    surah_number: int, 
    surah_name: str, 
    reciter: str, 
    scheduled_time=None,
    job_type: str = "standard",
    start_verse: int = None,
    end_verse: int = None,
    is_short: bool = False,
    upload_after_generation: bool = False,
    playlist_id: str = None,
    custom_title: str = None
):
    job = Job(
        surah_number=surah_number,
        surah_name=surah_name,
        reciter=reciter,
        scheduled_time=scheduled_time,
        job_type=job_type,
        start_verse=start_verse,
        end_verse=end_verse,
        is_short=1 if is_short else 0,
        upload_after_generation=1 if upload_after_generation else 0,
        playlist_id=playlist_id,
        custom_title=custom_title
    )
    session.add(job)
    await session.commit()
    return job

async def get_all_jobs(session: AsyncSession):
    result = await session.execute(select(Job).order_by(Job.id.desc())) # Newest first
    return result.scalars().all()

async def update_job_progress(session: AsyncSession, job_id: int, progress: float):
    job = await session.get(Job, job_id)
    if job:
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
    # Use surah_name to store the details for manual upload for now to keep it consistent
    # with how it's handled in worker, but set job_type correctly.
    data = {
        "video_filename": video_filename,
        "playlist_id": playlist_id,
        "details_filename": details_filename
    }
    job = Job(
        surah_number=0,
        surah_name=json.dumps(data),
        reciter=reciter_key,
        job_type="manual_upload",
        playlist_id=playlist_id
    )
    session.add(job)
    await session.commit()
    return job