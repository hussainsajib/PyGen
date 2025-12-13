
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
