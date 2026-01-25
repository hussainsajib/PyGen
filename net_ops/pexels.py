import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
BASE_URL = "https://api.pexels.com/videos"

async def search_pexels_videos(query: str, per_page: int = 15, page: int = 1, orientation: str = None):
    """
    Searches Pexels for videos.
    Returns a list of dicts with id, preview, and video_url.
    """
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY not found in environment variables.")
        return []

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": per_page,
        "page": page,
        "size": "medium" # reasonable size
    }
    
    if orientation and orientation != "any":
        params["orientation"] = orientation

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/search", headers=headers, params=params)
            if response.status_code != 200:
                print(f"Pexels API Error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            videos = []
            for video in data.get("videos", []):
                # Find the best quality video link (HD)
                video_files = video.get("video_files", [])
                # Sort by resolution (width) descending to get best quality
                video_files.sort(key=lambda x: x.get("width", 0), reverse=True)
                
                # Pick the first one (highest res) or fallback
                best_video = video_files[0] if video_files else None
                
                if best_video:
                    videos.append({
                        "id": video["id"],
                        "preview": video["image"], # Thumbnail
                        "video_url": best_video["link"],
                        "duration": video.get("duration"),
                        "width": best_video.get("width"),
                        "height": best_video.get("height")
                    })
            return videos
            
        except Exception as e:
            print(f"Error searching Pexels: {e}")
            return []
