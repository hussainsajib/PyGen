import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def upload_to_youtube(video_path):
    try:
        credentials, project = google.auth.default()
        youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        
        # Create the request for uploading the video
        request_body = {
            "snippet": {
                "title": "Quran Recitation Video",
                "description": "A recitation of selected verses from the Quran.",
                "tags": ["Quran", "Islam", "Recitation"],
                "categoryId": "28",
            },
            "status": {
                "privacyStatus": "public"
            }
        }
        
        with open(video_path, "rb") as video_file:
            request = youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=video_path
            )
            response = request.execute()
        
        return f"https://www.youtube.com/watch?v={response['id']}"
    
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
