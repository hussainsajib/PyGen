from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from db.models.base import Base

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    video_path = Column(String, nullable=False)
    screenshot_path = Column(String, nullable=True)
    details_path = Column(String, nullable=True)
    
    surah_number = Column(Integer, nullable=False)
    start_ayah = Column(Integer, nullable=True)
    end_ayah = Column(Integer, nullable=True)
    reciter_key = Column(String, nullable=False)
    
    generation_status = Column(String, default="success") # success, failed
    youtube_upload_status = Column(String, default="pending") # pending, uploaded
    youtube_video_id = Column(String, nullable=True)
    
    file_size = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MediaAsset(id={self.id}, surah={self.surah_number}, reciter={self.reciter_key})>"
