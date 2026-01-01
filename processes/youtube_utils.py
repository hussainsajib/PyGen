import os
import json
import time
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from moviepy.editor import VideoFileClip

RELEASE_INCREMENT = 1  # Increment the release date by this many days
TIMESTAMP_FILE = "video_release_date.txt"
TIMEZONE = ZoneInfo("America/New_York")

# Set up the API service
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
# ...

# Set up the API service
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
ACTUAL_CLIENT_SECRETS_FILE = "client_info.json" # Use the correct file as specified by the user
TOKEN_STORE_FILE = "youtube_tokens.json"


def get_authenticated_service(target_channel_id: str = None): # New parameter
    credentials = None
    all_tokens = _read_token_data()

    if target_channel_id:
        token_info = all_tokens.get(target_channel_id)
        if token_info:
            credentials = Credentials.from_authorized_user_info(json.loads(token_info))


    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                ACTUAL_CLIENT_SECRETS_FILE, 
                scopes
            )
            credentials = flow.run_local_server(port=8080) # This will store token in credentials object
        
        # Save updated credentials
        if target_channel_id:
            all_tokens[target_channel_id] = credentials.to_json()
            _write_token_data(all_tokens)

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
# The client_secrets_file (actual_client_secrets.json) should be in the root directory
# For this task, client_info.json will store the tokens.
TOKEN_STORE_FILE = "client_info.json"


def _read_token_data():
    """Reads token data from TOKEN_STORE_FILE."""
    if os.path.exists(TOKEN_STORE_FILE):
        try:
            with open(TOKEN_STORE_FILE, "r") as f:
                content = f.read()
                # Check if file is not empty before trying to load
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read token file '{TOKEN_STORE_FILE}'. It might be empty or corrupted. A new one will be created. Error: {e}")
            return {}
            return {}
    else:
        return {}

def _write_token_data(data):
    """Writes token data to TOKEN_STORE_FILE."""
    with open(TOKEN_STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Set up the API service
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_video_details(info_file_path: str):
    # Read the video details from the info file
    with open(info_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        title = lines[0].strip()
        
        # Description is everything between title and TAGS:
        description_lines = []
        tags = ["tag1", "tag2"]
        
        found_tags = False
        for line in lines[1:]:
            if line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                tags = [t.strip() for t in tags_str.split(",")]
                found_tags = True
                continue
            if not found_tags:
                description_lines.append(line)
        
        description = ''.join(description_lines).strip()
        return title, description, tags

def read_last_upload_time():
    try:
        with open(TIMESTAMP_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return datetime.fromisoformat(content)
    except (FileNotFoundError, ValueError):
        print("Timestamp file not found or invalid.")
    return None

def write_new_upload_time(timestamp: datetime):
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(timestamp.isoformat())
        
def get_release_date():
    now = datetime.now(TIMEZONE)
    last_uploaded_at = read_last_upload_time()

    if not last_uploaded_at or last_uploaded_at < now:
        release_date = now
    else:
        release_date = last_uploaded_at + timedelta(days=RELEASE_INCREMENT)

    write_new_upload_time(release_date)
    return release_date

def initialize_upload_request(youtube, video_details: dict):
    title, description, tags = get_video_details(video_details["info"])
    relase_date = get_release_date()
    
    return youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # Category ID (e.g., 22 for People & Blogs)
            },
            "status": {
                "privacyStatus": "private",  # Can be public, unlisted, private
                "publishAt": relase_date.strftime("%Y-%m-%dT%H:%M:%SZ")
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
    

def upload_to_youtube(video_details: dict, target_channel_id: str = None, playlist_id: str = None):
    # Upload video
    youtube = get_authenticated_service(target_channel_id)
    success = True
    video_id = None
    
    # Upload the video file to YouTube
    try:
        request = initialize_upload_request(youtube, video_details)
        video_id = resumable_upload(request)
    except Exception as e:
        print(str(e))
        print("❌ Video upload failed")
        success = False
    else:
        print("✅ Video uploaded successfully")
        
    # Upload the thumbnail if this is not a short video
    if success and not video_details["is_short"]:
        time.sleep(30)
        try:
            upload_thumbnail(youtube, video_id, video_details["screenshot"])
        except Exception as e:
            print(str(e))
            print("❌ Thumbnail upload failed")
            success = False
        else:
            print("✅ Thumbnail added to video successfully")
    
    # Add video to playlist if applicable
    if success and not video_details["is_short"] and playlist_id:
        try:
            add_video_to_playlist(youtube, video_id, playlist_id)
        except Exception as e:
            print(str(e))
            print("❌ Video not added to playlist")
            success = False
        else:
            print(f"✅ Video added to playlist {playlist_id}: {video_id}")
    if success:    
        print(f"https://www.youtube.com/watch?v={video_id}")
    return video_id if success else None

def get_all_playlists(youtube):
    """Fetches all playlists for the authenticated user."""
    playlists = []
    next_page_token = None
    while True:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        playlists.extend(response.get("items", []))
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return playlists

def get_videos_from_playlist(youtube, playlist_id):
    """Fetches all video IDs from a specific playlist."""
    video_ids = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return video_ids

def update_video_privacy(youtube, video_id, privacy_status):
    """Updates the privacy status of a single video."""
    request = youtube.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": {
                "privacyStatus": privacy_status
            }
        }
    )
    request.execute()
    