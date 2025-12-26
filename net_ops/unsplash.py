import os
import requests
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"

def search_unsplash(query: str, per_page: int = 10):
    if not UNSPLASH_ACCESS_KEY:
        print("UNSPLASH_ACCESS_KEY not found in environment variables.")
        return []
    
    params = {
        "query": query,
        "per_page": per_page,
        "client_id": UNSPLASH_ACCESS_KEY
    }
    
    try:
        response = requests.get(UNSPLASH_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error searching Unsplash: {e}")
        return []

def download_unsplash_image(url: str, filename: str):
    background_dir = "background"
    if not os.path.exists(background_dir):
        os.makedirs(background_dir)
    
    filepath = os.path.join(background_dir, filename)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath
    except Exception as e:
        print(f"Error downloading Unsplash image: {e}")
        return None
