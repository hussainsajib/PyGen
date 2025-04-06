import requests
import tempfile
import os

from moviepy.editor import AudioFileClip
from concurrent.futures import ThreadPoolExecutor, as_completed



# Step 2: Download from signed URL and process with moviepy
def download_and_process_signed_url(blob_name, signed_url):
    response = requests.get(signed_url, stream=True)
    response.raise_for_status()

    suffix = os.path.splitext(blob_name)[1] or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        for chunk in response.iter_content(chunk_size=8192):
            temp_audio.write(chunk)
        temp_path = temp_audio.name

    try:
        clip = AudioFileClip(temp_path)
        duration = clip.duration
        clip.close()
    finally:
        os.remove(temp_path)

    return {
        "file": blob_name,
        "duration_seconds": duration
    }

def process_all_signed_urls(signed_urls, max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_and_process_signed_url, name, url): name
            for name, url in signed_urls.items()
        }
        for future in as_completed(futures):
            blob_name = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"✅ Processed: {blob_name}")
            except Exception as e:
                print(f"❌ Failed: {blob_name} — {e}")
    return results