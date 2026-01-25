import os
import requests
import tempfile
from tqdm import tqdm

def download_mp3_temp(url: str):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download: status {response.status_code}")

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1KB chunks

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading MP3") as progress_bar:
        for chunk in response.iter_content(block_size):
            if chunk:
                temp.write(chunk)
                progress_bar.update(len(chunk))

    temp.close()
    print(f"Temporary MP3 saved at: {temp.name}")
    return temp.name

def download_file(url: str, filename: str, target_dir: str = "background"):
    """
    Downloads a file from a URL to a specified directory with a given filename.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    file_path = os.path.join(target_dir, filename)
    
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download: status {response.status_code}")

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024 

    with open(file_path, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {filename}") as progress_bar:
        for chunk in response.iter_content(block_size):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
                
    return file_path

def cleanup_temp_file(file_path: str):
    try:
        os.remove(file_path)
        print(f"Temporary file {file_path} deleted.")
    except OSError as e:
        print(f"Error deleting temporary file {file_path}: {e}")
