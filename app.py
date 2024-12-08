import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.processes import create_and_post

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/create-video")
async def create_video(request: Request, surah: int, start_verse: int, end_verse: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(create_and_post, surah, start_verse, end_verse)
    return RedirectResponse(request.url_for("read_root"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    res = []
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            res.append(surah)
    res.sort(key=lambda x: x["number"])
    context = {"request": request, "surahs": res}
    return templates.TemplateResponse("index.html", context)
