import httpx
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FacebookClient:
    def __init__(self, page_access_token: str, page_id: str):
        self.page_access_token = page_access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v19.0"

    def upload_standard_video(self, video_path: str, title: str, description: str) -> Optional[str]:
        """Uploads a standard video to the Facebook Page."""
        url = f"{self.base_url}/{self.page_id}/videos"
        
        # Meta expects 'description' for the post body, and 'title' for the video title
        params = {
            "access_token": self.page_access_token,
            "title": title,
            "description": description
        }
        
        try:
            with open(video_path, 'rb') as f:
                files = {"source": f}
                response = httpx.post(url, params=params, files=files, timeout=None)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully uploaded standard video to Facebook. ID: {data.get('id')}")
                return data.get("id")
        except Exception as e:
            logger.error(f"Error uploading standard video to Facebook: {e}")
            return None

    def upload_reel(self, video_path: str, description: str) -> Optional[str]:
        """Uploads a Reel to the Facebook Page using the Reels API."""
        # 1. Initialize the upload session
        init_url = f"{self.base_url}/{self.page_id}/video_reels"
        params = {
            "access_token": self.page_access_token,
            "upload_phase": "start"
        }
        
        try:
            # Step 1: Initialize
            response = httpx.post(init_url, params=params)
            response.raise_for_status()
            data = response.json()
            video_id = data.get("video_id")
            upload_url = data.get("upload_url")
            
            # Step 2: Upload the file
            file_size = os.path.getsize(video_path)
            with open(video_path, 'rb') as f:
                # Meta Reels upload expects binary data in the body, plus specific headers
                headers = {
                    "Authorization": f"OAuth {self.page_access_token}",
                    "offset": "0",
                    "file_size": str(file_size)
                }
                upload_response = httpx.post(upload_url, content=f.read(), headers=headers, timeout=None)
                upload_response.raise_for_status()
            
            # Step 3: Publish the Reel
            publish_url = f"{self.base_url}/{self.page_id}/video_reels"
            publish_params = {
                "access_token": self.page_access_token,
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description
            }
            publish_response = httpx.post(publish_url, params=publish_params)
            publish_response.raise_for_status()
            
            logger.info(f"Successfully uploaded Reel to Facebook. ID: {video_id}")
            return video_id
            
        except Exception as e:
            logger.error(f"Error uploading Reel to Facebook: {e}")
            return None

    def upload_to_facebook(self, video_path: str, title: str, description: str) -> Optional[str]:
        """Unified entry point to upload a video, deciding between Reel and Standard based on duration/aspect ratio."""
        # For simplicity in this iteration, we use the filename/metadata to hint if it's a Reel
        # In a real scenario, we'd use moviepy/cv2 to check aspect ratio and duration
        
        # Check if it's likely a Reel (Shorts format)
        is_reel = False
        if "shorts" in video_path.lower() or "#Shorts" in description:
            is_reel = True
            
        if is_reel:
            return self.upload_reel(video_path, description)
        else:
            return self.upload_standard_video(video_path, title, description)
