
from sqlalchemy import Column, Integer, String, DateTime, Enum, Float
from sqlalchemy.sql import func
from db.models.base import Base
import enum

class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"
    paused = "paused"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, nullable=False)
    surah_name = Column(String, nullable=False)
    reciter = Column(String, nullable=False)
    scheduled_time = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(Enum(JobStatus), default=JobStatus.pending)
    progress = Column(Float, default=0.0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # New fields for YouTube integration and WBW
    job_type = Column(String(50), default="standard") # standard, wbw, manual_upload
    upload_after_generation = Column(Integer, default=0) # 0 for false, 1 for true
    playlist_id = Column(String(100), nullable=True)
    start_verse = Column(Integer, nullable=True)
    end_verse = Column(Integer, nullable=True)
    is_short = Column(Integer, default=0) # 0 for false, 1 for true
    custom_title = Column(String(100), nullable=True)
