import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Set up the API service
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"

def upload_to_youtube(video_path: str):
    # Authenticate and create the API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
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
                "publishAt": "2024-11-20T15:00:00Z"  # Schedule for later (ISO 8601 format)
            }
        },
        media_body=video_path
    )
    response = request.execute()

    return f"https://www.youtube.com/watch?v={response['id']}"
