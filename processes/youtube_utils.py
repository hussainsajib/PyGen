import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload


# Set up the API service
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_info.json"
playlist = {
    "mishary": "PLvbeiWY3e2Qe8VLdBCLe5HeheC00U7Wfa",
    "akhdar": "PLvbeiWY3e2Qe5KAoGBhsteMaYNV-4ZqNk"
}

def get_video_details(info_file_path: str):
    # Read the video details from the info file
    with open(info_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        title = lines[0].strip()
        description = ''.join(lines[1:]).strip()
        return title, description

def get_authenticated_service():
    # Authenticate and create the API client
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, 
        scopes
    )
    credentials = flow.run_local_server(port=8080)
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

def initialize_upload_request(youtube, video_details: dict):
    title, description = get_video_details(video_details["info"])
    return youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["tag1", "tag2"],
                "categoryId": "22"  # Category ID (e.g., 22 for People & Blogs)
            },
            "status": {
                "privacyStatus": "private",  # Can be public, unlisted, private
            }
        },
        media_body=MediaFileUpload(video_details["video"], chunksize=-1, resumable=True, mimetype="video/*")
    )


def resumable_upload(request):
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    return response["id"]

def upload_thumbnail(youtube, video_id, thumbnail_path):
    request = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path)
    )
    return request.execute()

def add_video_to_playlist(youtube, video_id, playlist_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    return response
    

def upload_to_youtube(video_details: str):
    # Upload video
    youtube = get_authenticated_service()
    success = True
    video_id = None
    playlist_id = playlist["akhdar"]
    try:
        request = initialize_upload_request(youtube, video_details)
        video_id = resumable_upload(request)
    except Exception as e:
        print(str(e))
        success = False
    else:
        print("✅ Video uploaded successfully")
        
    if success:
        try:
            upload_thumbnail(youtube, video_id, video_details["screenshot"])
        except Exception as e:
            print(str(e))
            success = False
        else:
            print("✅ Thumbnail added to video successfully")
            
    if success:
        try:
            add_video_to_playlist(youtube, video_id, playlist_id)
        except Exception as e:
            print(str(e))
            success = False
        else:
            print(f"✅ Video added to playlist {playlist_id}: {video_id}")
        
    print(f"https://www.youtube.com/watch?v={video_id}")
