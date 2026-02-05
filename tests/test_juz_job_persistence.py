import pytest
from unittest.mock import MagicMock, AsyncMock
from db_ops.crud_jobs import enqueue_job
from db.models import Job

@pytest.mark.asyncio
async def test_enqueue_juz_job_with_pages():
    """Verify that a Juz job can be enqueued with start and end page parameters."""
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()
    
    surah_number = 1 # Overloaded for Juz
    surah_name = "Juz 1"
    reciter = "ar.alafasy"
    start_page = 1
    end_page = 5
    
    job = await enqueue_job(
        mock_session,
        surah_number=surah_number,
        surah_name=surah_name,
        reciter=reciter,
        job_type="juz_video",
        start_page=start_page,
        end_page=end_page
    )
    
    assert job.surah_number == surah_number
    assert job.job_type == "juz_video"
    assert job.start_page == start_page
    assert job.end_page == end_page
    mock_session.add.assert_called_with(job)
    mock_session.commit.assert_called_once()
