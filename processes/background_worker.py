from db.models import Job, JobStatus
from sqlalchemy import select
from db.database import async_session
import asyncio
import logging
import json
from processes.processes import create_surah_video, manual_upload_to_youtube, create_wbw_video_job
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def job_worker():
    while True:
        async with async_session() as session:
            result = await session.execute(
                select(Job).where(Job.status == JobStatus.pending).order_by(Job.created_at).limit(1)
            )
            job: Job = result.scalar_one_or_none()

            if job:
                logger.info(f"Processing job: {job.id} (Type: {job.job_type}) for Surah {job.surah_number} by {job.reciter}")
                job.status = JobStatus.processing
                await session.commit()

                try:
                    if job.job_type == "manual_upload" or (job.surah_number == 0 and job.job_type == "standard"):
                        # Manual upload job (checking both for backward compatibility)
                        data = json.loads(job.surah_name)
                        await manual_upload_to_youtube(
                            video_filename=data["video_filename"],
                            reciter_key=job.reciter,
                            playlist_id=data["playlist_id"],
                            details_filename=data["details_filename"]
                        )
                    elif job.job_type == "wbw":
                        # Word-by-word video generation job
                        await create_wbw_video_job(
                            surah=job.surah_number,
                            start_verse=job.start_verse,
                            end_verse=job.end_verse,
                            reciter=job.reciter,
                            is_short=bool(job.is_short),
                            upload_after_generation=bool(job.upload_after_generation),
                            playlist_id=job.playlist_id,
                            custom_title=job.custom_title
                        )
                    else:
                        # Standard full surah generation job
                        await create_surah_video(job.surah_number, job.reciter, custom_title=job.custom_title)

                    job.progress = 100.0
                    job.status = JobStatus.done
                    await session.commit()

                except Exception as e:
                    logger.error(f"Job {job.id} failed: {e}")
                    job.retry_count += 1
                    if job.retry_count >= job.max_retries:
                        job.status = JobStatus.failed
                    else:
                        job.status = JobStatus.pending
                    await session.commit()

            else:
                await asyncio.sleep(5) # Reduced sleep for better responsiveness

 