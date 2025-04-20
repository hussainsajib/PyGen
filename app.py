import os
import json
import asyncio

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import init_db, get_db
from processes.processes import create_and_post, create_surah_video
from processes.background_worker import job_worker
from db_ops.crud_jobs import get_all_jobs, enqueue_job

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(job_worker())
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/create-video", name="index")
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

@app.get("/surah", name="surah", response_class=HTMLResponse)
def create_surah(request: Request, background_tasks: BackgroundTasks):
    surahs = []
    reciters = []
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah_data = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah_data)
    surahs.sort(key=lambda x: x["number"])
    
    with open("data/reciter_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            if "database" in v.keys():
                reciters.append({
                        "english_name": v["english_name"],
                        "key": k
                })
    reciters.sort(key=lambda x: x["english_name"])
    
    context = {"request": request, "surahs": surahs, "reciters": reciters}
    return templates.TemplateResponse("surah.html", context)

@app.get("/create-surah-video", name="create_surah_video")
async def create_surah(request: Request, 
                 surah_number: int, 
                 reciter: str,
                 db: AsyncSession = Depends(get_db)
    ):
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        surah_name = data[str(surah_number)]["english_name"]
    job = await enqueue_job(db, surah_number, surah_name=surah_name, reciter=reciter)
    #background_tasks.add_task(create_surah_video, surah_number, reciter)
    return RedirectResponse(request.url_for("surah"))

@app.get("/jobs", name="jobs", response_class=HTMLResponse)
async def view_jobs(request: Request, db: AsyncSession = Depends(get_db)):
    jobs = await get_all_jobs(db)
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs})


@app.get("/tafseer", name="tafseer", response_class=HTMLResponse)
def tafseer(request: Request):
    surahs = []
    tafseer_data = []
    with open("data/tafseer_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            tafseer_data.append({"key": k, "name": v["name"]})
            
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah_data = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah_data)
    surahs.sort(key=lambda x: x["number"])
    return templates.TemplateResponse("tafseer.html", {"request": request, "tafseers": tafseer_data, "surahs": surahs})