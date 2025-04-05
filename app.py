import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from functools import lru_cache

from processes.processes import create_and_post
from config import Settings

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@lru_cache
def get_settings():
    return Settings()

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/create-video")
def create_video(request: Request, background_tasks: BackgroundTasks, 
                 surah: int, start_verse: int, end_verse: int, reciter: str,
                 is_short: bool = False):
    background_tasks.add_task(create_and_post, surah, start_verse, end_verse, reciter, is_short)
    return RedirectResponse(request.url_for("read_root"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    surahs = []
    reciters = []

    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah)
    surahs.sort(key=lambda x: x["number"])

    with open("data/reciter_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            if "folder" in v.keys():
                reciters.append({
                        "english_name": v["english_name"],
                        "key": k
                })
    reciters.sort(key=lambda x: x["english_name"])
    context = {"request": request, "surahs": surahs, "reciters": reciters}
    return templates.TemplateResponse("index.html", context)
