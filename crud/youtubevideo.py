from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from dataclasses import asdict

from models import YouTubeVideo
from processes.Classes.youtubevideo import YoutubeVideoDC

async def add_youtubevideo_record(
    session: AsyncSession,
    yt_video: YoutubeVideoDC
):
    new_video = YouTubeVideo(**asdict(yt_video))
    session.add(new_video)
    await session.commit()
    await session.refresh(new_video)
    return new_video