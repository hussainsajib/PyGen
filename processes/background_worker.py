from db.models import Job, JobStatus
from sqlalchemy import select
from db.database import async_session
import asyncio
import logging
import json
from processes.processes import create_surah_video, manual_upload_to_youtube
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
                logger.info(f"Processing job: {job.id} for Surah {job.surah_number} by {job.reciter}")
                job.status = JobStatus.processing
                await session.commit()

                try:
                    if job.surah_number == 0:
                        # Manual upload job
                        data = json.loads(job.surah_name)
                        await run_in_threadpool(
                            manual_upload_to_youtube,
                            video_filename=data["video_filename"],
                            reciter_key=job.reciter,
                            playlist_id=data["playlist_id"],
                            details_filename=data["details_filename"]
                        )
                    else:
                        # Standard video generation job
                        await run_in_threadpool(create_surah_video, job.surah_number, job.reciter)

                    job.progress = 100.0
                    job.status = JobStatus.done
                    await session.commit()

                except Exception as e:
                    job.retry_count += 1
                    if job.retry_count >= job.max_retries:
                        job.status = JobStatus.failed
                    else:
                        job.status = JobStatus.pending
                    await session.commit()

            else:
                await asyncio.sleep(10)
 