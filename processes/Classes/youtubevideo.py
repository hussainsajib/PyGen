from dataclasses import dataclass
from datetime import datetime

@dataclass
class YoutubeVideoDC:
    surah_number: int
    start_verse: int
    end_verse: int
    reciter_tag: str
    
    video_title: str
    video_description: str
    video_path: str
    youtube_id: str
    playlist_id: str
    
    thumbnail_name: str
    thumbnail_details: str
    
    privacy_status: str
    scheduled_time: datetime
    
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime