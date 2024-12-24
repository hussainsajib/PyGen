import os
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import googleapiclient.discovery
import googleapiclient.errors


# Set up the API service
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_info.json"

def upload_to_youtube(video_path: str):
    # Authenticate and create the API client
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, 
        scopes, 
        redirect_uri="http://localhost:8080/ flowName=GeneralOAuthFlow"
    )
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    # Upload video
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Your Video Title",
                "description": "This is a description of the video.",
                "tags": ["tag1", "tag2"],
                "categoryId": "22"  # Category ID (e.g., 22 for People & Blogs)
            },
            "status": {
                "privacyStatus": "private",  # Can be public, unlisted, private
                "publishAt": "2025-1-20T15:00:00Z"  # Schedule for later (ISO 8601 format)
            }
        },
        media_body=video_path
    )
    response = request.execute()

    print(f"https://www.youtube.com/watch?v={response['id']}")
