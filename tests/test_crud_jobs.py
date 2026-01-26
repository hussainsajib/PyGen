import pytest
from unittest.mock import AsyncMock, MagicMock
from db.models import Job
from db_ops.crud_jobs import enqueue_job, get_all_jobs, delete_single_job, retry_job

@pytest.mark.asyncio
async def test_enqueue_job_mushaf():
    """Test enqueuing a mushaf video job."""
    mock_session = AsyncMock()
    
    await enqueue_job(
        mock_session,
        surah_number=1,
        surah_name="Al-Fatihah",
        reciter="ar.alafasy",
        job_type="mushaf_video",
        is_short=False,
        background_path="test_bg.png"
    )
    
    mock_session.add.assert_called_once()
    added_job = mock_session.add.call_args[0][0]
    
    assert isinstance(added_job, Job)
    assert added_job.surah_number == 1
    assert added_job.job_type == "mushaf_video"
    assert added_job.background_path == "test_bg.png"
    assert added_job.is_short == 0
    
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_all_jobs():
    """Test retrieving all jobs."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [Job(id=1), Job(id=2)]
    mock_session.execute.return_value = mock_result
    
    jobs = await get_all_jobs(mock_session)
    
    assert len(jobs) == 2
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_retry_job():
    """Test retrying a job."""
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_session.get.return_value = mock_job
    
    await retry_job(mock_session, 1)
    
    assert mock_job.status == "pending"
    assert mock_job.progress == 0.0
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_single_job():
    """Test deleting a job."""
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_session.get.return_value = mock_job
    
    await delete_single_job(mock_session, 1)
    
    mock_session.delete.assert_awaited_once_with(mock_job)
    mock_session.commit.assert_awaited_once()
