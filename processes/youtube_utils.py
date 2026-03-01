import os
import json
import time
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Configuration
RELEASE_INCREMENT = 1  # Increment the release date by this many days
TIMESTAMP_FILE = "video_release_date.txt"
TIMEZONE = ZoneInfo("America/New_York")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_INFO_FILE = "client_info.json"

# Set insecure transport for local testing if needed
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def _read_token_data():
    """Reads all token data from CLIENT_INFO_FILE."""
    if os.path.exists(CLIENT_INFO_FILE):
        try:
            with open(CLIENT_INFO_FILE, "r") as f:
                content = f.read()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read '{CLIENT_INFO_FILE}': {e}")
    return {}

def _write_token_data(data):
    """Writes all token data back to CLIENT_INFO_FILE."""
    with open(CLIENT_INFO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_authenticated_service(target_channel_id: str = None, force_reauth: bool = False):
    """
    Returns an authenticated YouTube service object.
    Handles token loading, refreshing, and manual re-authentication if necessary.
    """
    credentials = None
    all_data = _read_token_data()

    # 1. Try to load existing credentials for the channel
    if target_channel_id and not force_reauth:
        token_info_str = all_data.get(target_channel_id)
        if token_info_str:
            try:
                # The token info is stored as a JSON string in our format
                token_info = json.loads(token_info_str)
                credentials = Credentials.from_authorized_user_info(token_info)
            except (json.JSONDecodeError, ValueError, KeyError):
                credentials = None

    # 2. Refresh or Re-authenticate if needed
    needs_auth = not credentials or not credentials.valid or force_reauth
    
    if credentials and credentials.expired and credentials.refresh_token and not force_reauth:
        try:
            print(f"INFO: Refreshing token for channel {target_channel_id}...")
            credentials.refresh(Request())
            needs_auth = False
        except RefreshError:
            print(f"INFO: Refresh token expired or invalid for {target_channel_id}. Re-authenticating...")
            needs_auth = True

    if needs_auth:
        print("INFO: Initiating OAuth flow. Please complete authentication in your browser.", flush=True)
        # Load client secrets from the same file that stores tokens (as it contains the 'web' key)
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_INFO_FILE, SCOPES)
        try:
            # This starts a local server and opens the browser
            credentials = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
            print("INFO: Authentication successful.")
        except Exception as e:
            print(f"ERROR: Failed to run local server for auth: {e}", flush=True)
            if "'NoneType' object has no attribute 'replace'" in str(e):
                print("HINT: This error often happens if the browser was closed before authentication was completed or if the redirect failed.")
            raise e

        # 3. Save the new credentials if we have a channel ID
        if target_channel_id and credentials:
            all_data[target_channel_id] = credentials.to_json()
            _write_token_data(all_data)

    if not credentials:
        raise Exception("Failed to obtain valid credentials.")

    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def refresh_channel_token(channel_id: str):
    """Forces re-authentication for a specific channel ID."""
    print(f"INFO: Forcing re-authentication for channel_id: {channel_id}")
    get_authenticated_service(target_channel_id=channel_id, force_reauth=True)

def get_video_details(info_file_path: str):
    """Reads video details (title, description, tags) from a file."""
    with open(info_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if not lines:
            return "Untitled", "", []
            
        title = lines[0].strip()
        
        description_lines = []
        tags = []
        found_tags = False
        
        for line in lines[1:]:
            if line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                found_tags = True
                continue
            if not found_tags:
                description_lines.append(line)
        
        description = ''.join(description_lines).strip()
        return title, description, tags

def read_last_upload_time():
    """Reads the last upload timestamp from TIMESTAMP_FILE."""
    try:
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return datetime.fromisoformat(content)
    except (FileNotFoundError, ValueError):
        pass
    return None

def write_new_upload_time(timestamp: datetime):
    """Writes the new upload timestamp to TIMESTAMP_FILE."""
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(timestamp.isoformat())
        
def get_release_date():
    """Calculates the scheduled release date for the next video."""
    now = datetime.now(TIMEZONE)
    last_uploaded_at = read_last_upload_time()

    if not last_uploaded_at or last_uploaded_at < now:
        release_date = now
    else:
        release_date = last_uploaded_at + timedelta(days=RELEASE_INCREMENT)

    write_new_upload_time(release_date)
    return release_date

def initialize_upload_request(youtube, video_details: dict):
    """Initializes the YouTube video upload request."""
    title, description, tags = get_video_details(video_details["info"])
    release_date = get_release_date()
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": release_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    
    media = MediaFileUpload(
        video_details["video"], 
        chunksize=-1, 
        resumable=True, 
        mimetype="video/*"
    )
    
    return youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

def resumable_upload(request):
    """Performs the resumable upload."""
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    return response["id"]

def upload_thumbnail(youtube, video_id, thumbnail_path):
    """Uploads a thumbnail for a video."""
    request = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path)
    )
    return request.execute()

def add_video_to_playlist(youtube, video_id, playlist_id):
    """Adds a video to a specific playlist."""
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
    return request.execute()

def upload_to_youtube(video_details: dict, target_channel_id: str = None, playlist_id: str = None):
    """Main function to upload a video to YouTube with all metadata."""
    try:
        youtube = get_authenticated_service(target_channel_id)
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

    video_id = None
    success = True
    
    # 1. Upload video
    try:
        request = initialize_upload_request(youtube, video_details)
        video_id = resumable_upload(request)
        print("✅ Video uploaded successfully")
    except Exception as e:
        print(f"❌ Video upload failed: {e}")
        success = False
    
    if not success:
        return None

    # 2. Upload thumbnail (if not a short)
    if not video_details.get("is_short"):
        time.sleep(5)  # Brief wait for video processing
        try:
            if video_details.get("screenshot"):
                upload_thumbnail(youtube, video_id, video_details["screenshot"])
                print("✅ Thumbnail added successfully")
        except Exception as e:
            print(f"⚠️ Thumbnail upload failed: {e}")
    
    # 3. Add to playlist
    if playlist_id:
        try:
            add_video_to_playlist(youtube, video_id, playlist_id)
            print(f"✅ Video added to playlist: {playlist_id}")
        except Exception as e:
            print(f"⚠️ Failed to add to playlist: {e}")
    
    print(f"🚀 Video URL: https://www.youtube.com/watch?v={video_id}")
    return video_id

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
    return request.execute()
