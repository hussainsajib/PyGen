from sqlalchemy import Column, Integer, String, DateTime, Boolean

from .base import Base


class YouTubeVideo(Base):
    __tablename__ = "YouTubeVideo"

    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, nullable=False)
    start_verse = Column(Integer, nullable=False)
    end_verse = Column(Integer, nullable=False)
    reciter_tag = Column(String, nullable=False)
    is_short = Column(Boolean, nullable=False, default=False)
    
    video_title = Column(String, nullable=False)
    video_description = Column(String, nullable=True)
    video_path = Column(String, nullable=False)
    youtube_id = Column(String, nullable=True)
    playlist_id = Column(String, nullable=True)
    
    thumbnail_name = Column(String, nullable=True)
    thumbnail_details = Column(String, nullable=True)
    
    privacy_status = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    
    uploaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)