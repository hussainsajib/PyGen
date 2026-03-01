import os
import json
import asyncio
import time
from typing import Optional
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Request, Depends, Form, Header, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import init_db, get_db, async_session
from processes.processes import create_and_post, create_surah_video
from processes.background_worker import job_worker, logger
from db_ops.crud_jobs import (
    get_all_jobs, 
    enqueue_job,
    clear_completed_jobs,
    delete_single_job,
    retry_job,
    enqueue_manual_upload_job,
    enqueue_fb_manual_upload_job
)
from db_ops import crud_reciters, crud_mushaf
from db_ops.crud_language import get_all_languages, get_translations_for_language
from db.models.language import Language
from sqlalchemy import select
from config_manager import ConfigManager, config_manager, get_config_manager
from processes.youtube_utils import (
    get_authenticated_service,
    get_all_playlists,
    get_videos_from_playlist,
    update_video_privacy,
    refresh_channel_token,
)
from net_ops.unsplash import search_unsplash, download_unsplash_image
from net_ops.pexels import search_pexels_videos
from net_ops.download_file import download_file
from factories.image_generator import ImageGenerator
from db_ops.crud_wbw import get_wbw_text_for_ayah
from db_ops.crud_text import get_full_translation_for_ayah
from db_ops.crud_surah import get_surah_by_number
from fastapi.responses import FileResponse, Response
import io

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

ligature_data = {}
with open("databases/text/ligatures.json", "r", encoding="utf-8") as f:
    ligature_data = json.load(f)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    # Load configuration values into memory using the config manager
    async with async_session() as session:
        await config_manager.load_from_db(session)
    
    asyncio.create_task(job_worker())
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
# Mount the Mushaf fonts directory under a unique path
app.mount("/mushaf-fonts", StaticFiles(directory="QPC_V2_Font.ttf"), name="mushaf_fonts")
templates = Jinja2Templates(directory="templates")



from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/mushaf", name="mushaf", response_class=HTMLResponse)
async def view_mushaf(request: Request, page: int = 1):
    # Fetch page data
    page_data = await run_in_threadpool(crud_mushaf.get_mushaf_page_data_structured, page)
    
    context = {
        "request": request,
        "page_data": page_data,
        "current_page": page,
        "total_pages": 604,
        "ligature_data": ligature_data
    }
    return templates.TemplateResponse("mushaf.html", context)


@app.get("/create-mushaf-video")
async def create_mushaf_video(
    surah: int,
    reciter: str,
    active_background: str = None, # Alias for background_path from UI
    is_short: bool = False,
    playlist_id: str = None,
    custom_title: str = None,
    upload_after_generation: bool = False,
    lines_per_page: int = 15,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    background_path = active_background
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        surah_name = data[str(surah)]["english_name"]

    # Respect global config
    final_upload = upload_after_generation
    if config.get("UPLOAD_TO_YOUTUBE") == "True":
        final_upload = True

    await enqueue_job(
        db,
        surah_number=surah,
        surah_name=surah_name,
        reciter=reciter,
        job_type="mushaf_video",
        is_short=is_short,
        background_path=background_path,
        playlist_id=playlist_id if playlist_id != "none" else None,
        custom_title=custom_title,
        upload_after_generation=final_upload,
        lines_per_page=lines_per_page
    )
    return RedirectResponse(url="/jobs", status_code=303)

@app.get("/create-mushaf-fast/{engine}")
async def create_mushaf_fast_route(
    engine: str,
    reciter: str,
    surah: Optional[int] = None,
    juz: Optional[int] = None,
    is_short: bool = False,
    is_juz: bool = False,
    active_background: str = None,
    playlist_id: str = None,
    upload_after_generation: bool = False,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    if engine not in ["ffmpeg", "opencv", "pyav"]:
        return HTMLResponse("Invalid engine type", status_code=400)
        
    target_num = juz if is_juz else surah
    if target_num is None:
        return HTMLResponse("Missing surah or juz number", status_code=400)

    surah_name = f"Fast {engine.upper()} - {'Juz' if is_juz else 'Surah'} {target_num}"
    if not is_juz:
        with open("data/surah_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            surah_name = data[str(target_num)]["english_name"]
            
    # Respect global config
    final_upload = upload_after_generation
    if config.get("UPLOAD_TO_YOUTUBE") == "True":
        final_upload = True

    from db_ops.crud_jobs import enqueue_job
    await enqueue_job(
        db,
        surah_number=target_num,
        surah_name=surah_name,
        reciter=reciter,
        job_type="mushaf_fast",
        is_short=is_short,
        background_path=active_background,
        engine_type=engine,
        custom_title="juz" if is_juz else "surah",
        upload_after_generation=final_upload,
        playlist_id=playlist_id if playlist_id != "none" else None
    )
    return RedirectResponse(url="/jobs", status_code=303)

@app.get("/create-video")
async def create_video(
    request: Request, 
    surah: int, 
    start_verse: int, 
    end_verse: int, 
    reciter: str,
    active_background: str = None,
    is_short: bool = False,
    job_type: str = "standard",
    upload_after_generation: bool = False,
    playlist_id: str = None,
    custom_title: str = None,
    engine_type: str = "moviepy",
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    background_path = active_background
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        surah_name = data[str(surah)]["english_name"]
        
    # If global upload is on, and it's a WBW job, we default to upload unless specifically overridden
    # For now, if UPLOAD_TO_YOUTUBE is true, we set it to true for the job.
    final_upload = upload_after_generation
    if job_type == "wbw":
        if config.get("UPLOAD_TO_YOUTUBE") == "True":
            final_upload = True
        else:
            # If global config is off, force off, ignoring potential stale UI inputs
            final_upload = False

    await enqueue_job(
        db, 
        surah, 
        surah_name=surah_name, 
        reciter=reciter,
        job_type=job_type,
        start_verse=start_verse,
        end_verse=end_verse,
        is_short=is_short,
        upload_after_generation=final_upload,
        playlist_id=playlist_id,
        custom_title=custom_title,
        background_path=background_path,
        engine_type=engine_type
    )
    if job_type == "wbw":
        if engine_type == "ffmpeg":
            return RedirectResponse(request.url_for("wbw_fast"))
        return RedirectResponse(request.url_for("wbw"))
    return RedirectResponse(request.url_for("index"))

@app.get("/", name="index", response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    surahs = []
    reciters = []

    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah)
    surahs.sort(key=lambda x: x["number"])

    # Load reciters from database that have a 'database' entry
    db_reciters = await crud_reciters.get_all_reciters(db)
    for r in db_reciters:
        if r.database:
            reciters.append({
                "english_name": r.english_name,
                "key": r.reciter_key
            })
    reciters.sort(key=lambda x: x["english_name"])
    
    context = {"request": request, "surahs": surahs, "reciters": reciters}
    return templates.TemplateResponse("index.html", context)

@app.get("/mushaf-video", name="mushaf_video_creator", response_class=HTMLResponse)
async def mushaf_video_interface(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    surahs = []
    reciters = []

    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah)
    surahs.sort(key=lambda x: x["number"])

    db_reciters = await crud_reciters.get_all_reciters(db)
    
    playlists = []
    seen_playlists = set()
    for r in db_reciters:
        if r.playlist_id and r.playlist_id not in seen_playlists:
            playlists.append({"id": r.playlist_id, "name": f"Playlist {r.playlist_id} ({r.english_name})"})
            seen_playlists.add(r.playlist_id)
            
    for r in db_reciters:
        # Note: Mushaf video also needs WBW timestamps for highlighting
        if r.wbw_database and str(r.wbw_database).strip(): 
            reciters.append({
                "english_name": r.english_name,
                "key": r.reciter_key
            })
    reciters.sort(key=lambda x: x["english_name"])
    
    upload_to_youtube = config.get("UPLOAD_TO_YOUTUBE", "False") == "True"
    enable_facebook_upload = config.get("ENABLE_FACEBOOK_UPLOAD", "False") == "True"
    default_language = config.get("DEFAULT_LANGUAGE", "bengali")
    bg_rgb = config.get("BACKGROUND_RGB", "(0,0,0)")
    font_color = config.get("FONT_COLOR", "white")
    
    mushaf_bg_mode = config.get("MUSHAF_PAGE_BACKGROUND_MODE", "Solid")
    mushaf_bg_color = config.get("MUSHAF_PAGE_COLOR", "#FFFDF5")
    
    languages = await get_all_languages(db)
    
    context = {
        "request": request, 
        "surahs": surahs, 
        "reciters": reciters,
        "upload_to_youtube": upload_to_youtube,
        "enable_facebook_upload": enable_facebook_upload,
        "default_language": default_language,
        "bg_rgb": bg_rgb,
        "font_color": font_color,
        "mushaf_bg_mode": mushaf_bg_mode,
        "mushaf_bg_color": mushaf_bg_color,
        "languages": languages,
        "playlists": playlists
    }
    return templates.TemplateResponse("mushaf_video.html", context)

@app.get("/juz-video", name="juz_video_creator", response_class=HTMLResponse)
async def juz_video_interface(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    reciters = []
    db_reciters = await crud_reciters.get_all_reciters(db)
    
    playlists = []
    seen_playlists = set()
    for r in db_reciters:
        if r.playlist_id and r.playlist_id not in seen_playlists:
            playlists.append({"id": r.playlist_id, "name": f"Playlist {r.playlist_id} ({r.english_name})"})
            seen_playlists.add(r.playlist_id)
            
    for r in db_reciters:
        # Juz video needs WBW timestamps for highlighting
        if r.wbw_database and str(r.wbw_database).strip(): 
            reciters.append({
                "english_name": r.english_name,
                "key": r.reciter_key
            })
    reciters.sort(key=lambda x: x["english_name"])
    
    upload_to_youtube = config.get("UPLOAD_TO_YOUTUBE", "False") == "True"
    enable_facebook_upload = config.get("ENABLE_FACEBOOK_UPLOAD", "False") == "True"
    default_language = config.get("DEFAULT_LANGUAGE", "bengali")
    bg_rgb = config.get("BACKGROUND_RGB", "(0,0,0)")
    font_color = config.get("FONT_COLOR", "white")
    mushaf_bg_mode = config.get("MUSHAF_PAGE_BACKGROUND_MODE", "Solid")
    mushaf_bg_color = config.get("MUSHAF_PAGE_COLOR", "#FFFDF5")
    
    languages = await get_all_languages(db)
    
    context = {
        "request": request, 
        "reciters": reciters,
        "upload_to_youtube": upload_to_youtube,
        "enable_facebook_upload": enable_facebook_upload,
        "default_language": default_language,
        "bg_rgb": bg_rgb,
        "font_color": font_color,
        "mushaf_bg_mode": mushaf_bg_mode,
        "mushaf_bg_color": mushaf_bg_color,
        "languages": languages,
        "playlists": playlists
    }
    return templates.TemplateResponse("juz_video.html", context)

@app.get("/create-juz-video")
async def create_juz_video(
    juz: int,
    reciter: str,
    active_background: str = None,
    is_short: bool = False,
    playlist_id: str = None,
    custom_title: str = None,
    upload_after_generation: bool = False,
    lines_per_page: int = 15,
    start_page: str = None,
    end_page: str = None,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    # Convert empty strings to None for integer fields
    s_page = int(start_page) if start_page and start_page.strip() else None
    e_page = int(end_page) if end_page and end_page.strip() else None

    # Respect global config
    final_upload = upload_after_generation
    if config.get("UPLOAD_TO_YOUTUBE") == "True":
        final_upload = True

    await enqueue_job(
        db,
        surah_number=juz, # We overload surah_number for Juz identification in juz_video type
        surah_name=f"Juz {juz}",
        reciter=reciter,
        job_type="juz_video",
        is_short=is_short,
        background_path=active_background,
        playlist_id=playlist_id if playlist_id != "none" else None,
        custom_title=custom_title,
        upload_after_generation=final_upload,
        lines_per_page=lines_per_page,
        start_page=s_page,
        end_page=e_page
    )
    return RedirectResponse(url="/jobs", status_code=303)

@app.get("/wbw-fast", name="wbw_fast", response_class=HTMLResponse)
async def wbw_fast_interface(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    surahs = []
    reciters = []

    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah)
    surahs.sort(key=lambda x: x["number"])

    # Load reciters who have a 'wbw_database' entry
    db_reciters = await crud_reciters.get_all_reciters(db)
    
    # Extract unique playlists from reciters
    playlists = []
    seen_playlists = set()
    for r in db_reciters:
        if r.playlist_id and r.playlist_id not in seen_playlists:
            playlists.append({"id": r.playlist_id, "name": f"Playlist {r.playlist_id} ({r.english_name})"})
            seen_playlists.add(r.playlist_id)
            
    for r in db_reciters:
        # Note: Mushaf video also needs WBW timestamps for highlighting
        if r.wbw_database and str(r.wbw_database).strip(): 
            reciters.append({
                "english_name": r.english_name,
                "key": r.reciter_key
            })
    reciters.sort(key=lambda x: x["english_name"])
    
    upload_to_youtube = config.get("UPLOAD_TO_YOUTUBE", "False") == "True"
    enable_facebook_upload = config.get("ENABLE_FACEBOOK_UPLOAD", "False") == "True"
    default_language = config.get("DEFAULT_LANGUAGE", "bengali")
    bg_rgb = config.get("BACKGROUND_RGB", "(0,0,0)")
    font_color = config.get("FONT_COLOR", "white")
    languages = await get_all_languages(db)
    
    context = {
        "request": request, 
        "surahs": surahs, 
        "reciters": reciters,
        "upload_to_youtube": upload_to_youtube,
        "enable_facebook_upload": enable_facebook_upload,
        "default_language": default_language,
        "bg_rgb": bg_rgb,
        "font_color": font_color,
        "languages": languages,
        "playlists": playlists
    }
    return templates.TemplateResponse("wbw_fast.html", context)

@app.get("/word-by-word", name="wbw", response_class=HTMLResponse)
async def wbw_interface(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    surahs = []
    reciters = []

    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah)
    surahs.sort(key=lambda x: x["number"])

    # Load reciters who have a 'wbw_database' entry
    db_reciters = await crud_reciters.get_all_reciters(db)
    
    # Extract unique playlists from reciters
    playlists = []
    seen_playlists = set()
    for r in db_reciters:
        if r.playlist_id and r.playlist_id not in seen_playlists:
            playlists.append({"id": r.playlist_id, "name": f"Playlist {r.playlist_id} ({r.english_name})"})
            seen_playlists.add(r.playlist_id)
            
    for r in db_reciters:
        # Note: Mushaf video also needs WBW timestamps for highlighting
        if r.wbw_database and str(r.wbw_database).strip(): 
            reciters.append({
                "english_name": r.english_name,
                "key": r.reciter_key
            })
    reciters.sort(key=lambda x: x["english_name"])
    
    upload_to_youtube = config.get("UPLOAD_TO_YOUTUBE", "False") == "True"
    enable_facebook_upload = config.get("ENABLE_FACEBOOK_UPLOAD", "False") == "True"
    default_language = config.get("DEFAULT_LANGUAGE", "bengali")
    bg_rgb = config.get("BACKGROUND_RGB", "(0,0,0)")
    font_color = config.get("FONT_COLOR", "white")
    languages = await get_all_languages(db)
    
    context = {
        "request": request, 
        "surahs": surahs, 
        "reciters": reciters,
        "upload_to_youtube": upload_to_youtube,
        "enable_facebook_upload": enable_facebook_upload,
        "default_language": default_language,
        "bg_rgb": bg_rgb,
        "font_color": font_color,
        "languages": languages,
        "playlists": playlists
    }
    return templates.TemplateResponse("wbw.html", context)

@app.get("/surah", name="surah", response_class=HTMLResponse)
async def create_surah(
    request: Request, 
    background_tasks: BackgroundTasks,
    config: ConfigManager = Depends(get_config_manager),
    db: AsyncSession = Depends(get_db)
):
    surahs = []
    reciters = []
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah_data = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah_data)
    surahs.sort(key=lambda x: x["number"])
    
    # Load reciters from database that have a 'database' entry
    db_reciters = await crud_reciters.get_all_reciters(db)
    for r in db_reciters:
        if r.database:
            reciters.append({
                "english_name": r.english_name,
                "key": r.reciter_key
            })
    reciters.sort(key=lambda x: x["english_name"])
    
    context = {
        "request": request, 
        "surahs": surahs, 
        "reciters": reciters, 
        "c_reciter": config.get("RECITER", "ar.alafasy")
    }
    return templates.TemplateResponse("surah.html", context)

@app.get("/create-surah-video", name="create_surah_video")
async def create_surah(request: Request, 
                 surah_number: int, 
                 reciter: str,
                 custom_title: str = None,
                 db: AsyncSession = Depends(get_db),
                 config: ConfigManager = Depends(get_config_manager)
    ):
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        surah_name = data[str(surah_number)]["english_name"]
    
    upload_after = False
    if config.get("UPLOAD_TO_YOUTUBE") == "True":
        upload_after = True
        
    await enqueue_job(db, surah_number, surah_name=surah_name, reciter=reciter, custom_title=custom_title, upload_after_generation=upload_after)
    return RedirectResponse(request.url_for("surah"))

@app.get("/create-all-surah-videos", name="create_all_surah_videos")
async def create_all_surah_videos(request: Request, 
                                reciter: str, 
                                db: AsyncSession = Depends(get_db),
                                config: ConfigManager = Depends(get_config_manager)
    ):
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    upload_after = False
    if config.get("UPLOAD_TO_YOUTUBE") == "True":
        upload_after = True

    for surah_number in range(1, 115):
        surah_name = data[str(surah_number)]["english_name"]
        print(f"Enqueuing job for Surah {surah_number}: {surah_name} with reciter {reciter}")
        await enqueue_job(db, surah_number, surah_name=surah_name, reciter=reciter, upload_after_generation=upload_after)
    
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

@app.post("/clear-jobs")
async def clear_jobs(db: AsyncSession = Depends(get_db)):
    await clear_completed_jobs(db)
    return RedirectResponse(url="/jobs", status_code=303)


@app.post("/delete-job/{job_id}", response_class=RedirectResponse)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    await delete_single_job(db, job_id)
    return RedirectResponse(url="/jobs", status_code=303)


@app.post("/retry-job/{job_id}", response_class=RedirectResponse)
async def retry_job_endpoint(job_id: int, db: AsyncSession = Depends(get_db)):
    print(f"Retrying job with ID: {job_id}")
    await retry_job(db, job_id)
    return RedirectResponse(url="/jobs", status_code=303)


@app.get("/config", response_class=HTMLResponse, name="config")
async def config_form(
    request: Request,
    config: ConfigManager = Depends(get_config_manager),
    db: AsyncSession = Depends(get_db)
):
    # Reload config from DB to ensure latest keys (like MUSHAF_PAGE_BACKGROUND_*) are visible
    await config.load_from_db(db, reload=True)
    
    # Load reciters for the dropdown
    reciters = []
    with open("data/reciter_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for key, info in data.items():
            if "database" in info:
                reciters.append({
                    "key": key,
                    "english_name": info["english_name"]
                })
    reciters.sort(key=lambda x: x["english_name"])

    # Get config items directly from the manager (already sorted)
    config_items = config.get_all()
    
    # Get available languages
    languages = await get_all_languages(db)
    
    # Get available translations for each language
    lang_translations = {}
    for lang in languages:
        translations = await get_translations_for_language(db, lang.id)
        lang_translations[lang.name] = [{"db_name": t.db_name, "display_name": t.display_name} for t in translations]

    
    return templates.TemplateResponse("config.html", {
        "request": request, 
        "config": config_items,
        "reciters": reciters,
        "languages": languages,
        "lang_translations_json": json.dumps(lang_translations) # Pass as JSON for JS
    })

@app.post("/config")
async def save_config(
    request: Request,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    form = await request.form()
    for key, value in form.items():
        await config.set(db, key, value)
    return RedirectResponse(url="/config", status_code=303)

@app.post("/config/new")
async def create_config(
    key: str = Form(...),
    value: str = Form(...),
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    await config.set(db, key, value)
    return RedirectResponse(url="/config", status_code=303)

@app.post("/config/delete/{key}", name="config_delete")
async def delete_config(
    key: str,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    await config.delete(db, key)
    return RedirectResponse(url="/config", status_code=303)

from pydantic import BaseModel

class ConfigUpdate(BaseModel):
    key: str
    value: str

@app.post("/config/update")
async def update_config_api(
    config_data: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    await config.set(db, config_data.key, config_data.value)
    return JSONResponse({"status": "success", "key": config_data.key, "value": config_data.value})

@app.post("/config/language/update")
async def update_language_font(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    form = await request.form()
    for key, value in form.items():
        if key.startswith("font_"):
            try:
                lang_id = int(key.split("_")[1])
                stmt = select(Language).where(Language.id == lang_id)
                result = await db.execute(stmt)
                lang = result.scalar_one_or_none()
                if lang:
                    lang.font = value
            except ValueError:
                continue
    await db.commit()
    return RedirectResponse(url="/config", status_code=303)

@app.post("/youtube/refresh-token")
async def youtube_refresh_token(
    language_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    lang_obj = await db.get(Language, language_id)
    if not lang_obj or not lang_obj.youtube_channel_id:
        return JSONResponse({"status": "error", "message": "Language or Channel ID not found."}, status_code=404)
    
    try:
        # Run in threadpool because it starts a local server and blocks
        await run_in_threadpool(refresh_channel_token, lang_obj.youtube_channel_id)
        return JSONResponse({"status": "success", "message": "Token refresh process initiated."})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/playlists", name="playlists", response_class=HTMLResponse)
async def view_playlists(request: Request):
    try:
        youtube = await run_in_threadpool(get_authenticated_service)
        playlists = await run_in_threadpool(get_all_playlists, youtube)
        return templates.TemplateResponse("playlists.html", {"request": request, "playlists": playlists})
    except Exception as e:
        logger.error(f"Could not fetch YouTube playlists: {e}")
        # You might want to render an error page or a message
        return templates.TemplateResponse("playlists.html", {"request": request, "playlists": [], "error": str(e)})

@app.post("/update-playlist-privacy", name="update_playlist_privacy")
async def update_playlist_privacy_endpoint(
    request: Request,
    playlist_id: str = Form(...),
    privacy_status: str = Form(...)
):
    try:
        youtube = await run_in_threadpool(get_authenticated_service)
        video_ids = await run_in_threadpool(get_videos_from_playlist, youtube, playlist_id)
        
        for video_id in video_ids:
            await run_in_threadpool(update_video_privacy, youtube, video_id, privacy_status)
            logger.info(f"Updated video {video_id} in playlist {playlist_id} to {privacy_status}")
    except Exception as e:
        logger.error(f"Failed to update playlist privacy: {e}")
        # Optionally, add a message to show the user something went wrong
    return RedirectResponse(url=request.url_for("playlists"), status_code=303)

# --- Reciter CRUD Endpoints ---

from processes.video_utils import discover_assets
from itertools import groupby

from db_ops import crud_media_assets

@app.get("/manual-upload", name="manual_upload", response_class=HTMLResponse)
async def manual_upload(request: Request, db: AsyncSession = Depends(get_db)):
    assets = await crud_media_assets.get_all_media_assets(db)
    reciters = await crud_reciters.get_all_reciters(db)
    
    reciter_map = {r.reciter_key: r for r in reciters}
    
    # Enrich assets with reciter info
    enriched_assets = []
    for asset in assets:
        reciter = reciter_map.get(asset.reciter_key)
        enriched_assets.append({
            "id": asset.id,
            "filename": asset.filename,
            "reciter": reciter.english_name if reciter else asset.reciter_key,
            "reciter_key": asset.reciter_key,
            "screenshot_present": asset.screenshot_present,
            "details_present": asset.details_present,
            "details_filename": os.path.basename(asset.details_path) if asset.details_path else "",
            "playlist_id": reciter.playlist_id if reciter else None,
            "playlist_status": reciter.playlist_id if reciter and reciter.playlist_id else "No Playlist"
        })
    
    # Sort enriched assets by reciter name for grouping
    enriched_assets.sort(key=lambda x: x["reciter"])
    
    # Group by reciter
    grouped_videos = {}
    for reciter_name, group in groupby(enriched_assets, key=lambda x: x["reciter"]):
        grouped_videos[reciter_name] = list(group)
        
    return templates.TemplateResponse(request, "manual_upload.html", {"grouped_videos": grouped_videos})


@app.post("/trigger-manual-upload", name="trigger_manual_upload")
async def trigger_manual_upload(
    request: Request,
    video_filename: str = Form(...),
    reciter_key: str = Form(...),
    playlist_id: str = Form(None),
    details_filename: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    await enqueue_manual_upload_job(db, video_filename, reciter_key, playlist_id, details_filename)
    return RedirectResponse(url=request.url_for("jobs"), status_code=303)


@app.post("/trigger-fb-manual-upload", name="trigger_fb_manual_upload")
async def trigger_fb_manual_upload(
    request: Request,
    video_filename: str = Form(...),
    details_filename: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    await enqueue_fb_manual_upload_job(db, video_filename, details_filename)
    return RedirectResponse(url=request.url_for("jobs"), status_code=303)


from fastapi.responses import FileResponse

@app.get("/view-asset/{asset_type}/{asset_id}", name="view_asset")
async def view_asset(asset_type: str, asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await crud_media_assets.get_media_asset_by_id(db, asset_id)
    if not asset:
        return HTMLResponse("Asset not found", status_code=404)
    
    path = None
    if asset_type == "video":
        path = asset.video_path
    elif asset_type == "screenshot":
        path = asset.screenshot_path
    elif asset_type == "details":
        path = asset.details_path
        # For details, we might want to return as text or wrap in HTML
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(f"<html><body><pre>{content}</pre></body></html>")
    
    if path and os.path.exists(path):
        return FileResponse(path)
    
    return HTMLResponse("File not found on disk", status_code=404)


@app.post("/delete-media/{asset_id}", name="delete_media")
async def delete_media(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await crud_media_assets.get_media_asset_by_id(db, asset_id)
    if asset:
        # Delete from disk
        paths = [asset.video_path, asset.screenshot_path, asset.details_path]
        for path in paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")
        
        # Delete from DB
        await crud_media_assets.delete_media_asset(db, asset_id)
        
    return RedirectResponse(url="/manual-upload", status_code=303)


@app.post("/delete-bulk-media", name="delete_bulk_media")
async def delete_bulk_media(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    asset_ids = form.getlist("asset_ids")
    
    for asset_id_str in asset_ids:
        asset_id = int(asset_id_str)
        asset = await crud_media_assets.get_media_asset_by_id(db, asset_id)
        if asset:
            # Delete from disk
            paths = [asset.video_path, asset.screenshot_path, asset.details_path]
            for path in paths:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        logger.error(f"Failed to delete {path}: {e}")
            
            # Delete from DB
            await crud_media_assets.delete_media_asset(db, asset_id)
            
    return RedirectResponse(url="/manual-upload", status_code=303)


@app.post("/upload-background")
async def upload_background(file: UploadFile = File(...)):
    background_dir = "background"
    if not os.path.exists(background_dir):
        os.makedirs(background_dir)
    
    file_path = os.path.join(background_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"filename": file.filename, "path": file_path}


    return RedirectResponse(url="/manual-upload", status_code=303)


@app.get("/unsplash-search")
async def unsplash_search(query: str, page: int = 1):
    results = await run_in_threadpool(search_unsplash, query, page, 20)
    return results

@app.post("/set-active-background")
async def set_active_background(
    path: str = Form(...),
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    await config.set(db, "ACTIVE_BACKGROUND", path)
    return {"status": "success", "active_background": path}

@app.post("/clear-active-background")
async def clear_active_background(
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    await config.set(db, "ACTIVE_BACKGROUND", "")
    return {"status": "success"}

@app.post("/download-unsplash")
async def download_unsplash(url: str = Form(...), filename: str = Form(...)):
    try:
        path = await run_in_threadpool(download_unsplash_image, url, filename)
        return JSONResponse({"status": "success", "path": path})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/pexels-search")
async def pexels_search(query: str, page: int = 1, orientation: str = None):
    videos = await search_pexels_videos(query, page=page, orientation=orientation)
    return JSONResponse(videos)

@app.post("/download-pexels-video")
async def download_pexels_video(url: str = Form(...), filename: str = Form(...)):
    try:
        path = await run_in_threadpool(download_file, url, filename, "background")
        return JSONResponse({"status": "success", "path": path})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/reciters", response_class=HTMLResponse, name="reciters_list")
async def list_reciters(request: Request, db: AsyncSession = Depends(get_db)):
    reciters = await crud_reciters.get_all_reciters(db)
    return templates.TemplateResponse("reciters.html", {"request": request, "reciters": reciters})

@app.get("/reciter/new", name="reciter_new_form", response_class=HTMLResponse)
async def reciter_new_form(request: Request):
    return templates.TemplateResponse(
        "reciter_form.html",
        {
            "request": request,
            "reciter": None,
            "action_url": request.url_for("reciter_create")
        }
    )

@app.post("/reciter/new", name="reciter_create")
async def reciter_create(request: Request, db: AsyncSession = Depends(get_db)):
    form_data = await request.form()
    data = dict(form_data)
    
    # Validation
    if not validate_wbw_exists(data.get("wbw_database")):
        return templates.TemplateResponse(
            request,
            "reciter_form.html",
            {
                "request": request,
                "reciter": data,
                "action_url": request.url_for("reciter_create"),
                "error": f"WBW Database file '{data.get('wbw_database')}' not found in databases/word-by-word/"
            }
        )
        
    await crud_reciters.create_reciter(db, data)
    return RedirectResponse(url=request.url_for("reciters_list"), status_code=303)

@app.get("/reciter/{reciter_id}/edit", name="reciter_edit_form", response_class=HTMLResponse)
async def reciter_edit_form(request: Request, reciter_id: int, db: AsyncSession = Depends(get_db)):
    reciter = await crud_reciters.get_reciter_by_id(db, reciter_id)
    return templates.TemplateResponse(
        "reciter_form.html",
        {
            "request": request,
            "reciter": reciter,
            "action_url": request.url_for("reciter_update", reciter_id=reciter_id)
        }
    )

@app.post("/reciter/{reciter_id}/edit", name="reciter_update")
async def reciter_update(request: Request, reciter_id: int, db: AsyncSession = Depends(get_db)):
    form_data = await request.form()
    data = dict(form_data)
    
    # Validation
    if not validate_wbw_exists(data.get("wbw_database")):
        reciter = await crud_reciters.get_reciter_by_id(db, reciter_id)
        # We merge form data with existing reciter for the template
        return templates.TemplateResponse(
            request,
            "reciter_form.html",
            {
                "request": request,
                "reciter": {**reciter.__dict__, **data, "id": reciter_id},
                "action_url": request.url_for("reciter_update", reciter_id=reciter_id),
                "error": f"WBW Database file '{data.get('wbw_database')}' not found in databases/word-by-word/"
            }
        )
        
    await crud_reciters.update_reciter(db, reciter_id, data)
    return RedirectResponse(url=request.url_for("reciters_list"), status_code=303)

@app.post("/reciter/{reciter_id}/delete", name="reciter_delete")
async def reciter_delete(request: Request, reciter_id: int, db: AsyncSession = Depends(get_db)):
    await crud_reciters.delete_reciter(db, reciter_id)
    return RedirectResponse(url=request.url_for("reciters_list"), status_code=303)


def validate_wbw_exists(filename: str):
    if not filename:
        return True # Optional field
    return os.path.exists(os.path.join("databases", "word-by-word", filename))

# --- Image Generator Endpoints ---

@app.get("/image-generator", name="image_generator", response_class=HTMLResponse)
async def image_generator_interface(
    request: Request,
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    surahs = []
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            surah = {"number": int(v["serial"]), "name": v["english_name"], "total_verses": v["total_ayah"]}
            surahs.append(surah)
    surahs.sort(key=lambda x: x["number"])

    active_bg = config.get("ACTIVE_BACKGROUND", "")
    default_hashtags = config.get("IMAGE_GEN_DEFAULT_HASHTAGS", "#Quran #TaqwaBangla #IslamicPost")
    bg_rgb = config.get("BACKGROUND_RGB", "(0,0,0)")
    font_color = config.get("FONT_COLOR", "white")

    return templates.TemplateResponse("image_generator.html", {
        "request": request,
        "surahs": surahs,
        "active_bg": active_bg,
        "default_hashtags": default_hashtags,
        "bg_rgb": bg_rgb,
        "font_color": font_color
    })

async def _internal_generate_image(surah: int, ayah: int, background_path: str = None):
    # 1. Get real data
    page_number = await run_in_threadpool(crud_mushaf.get_page_for_verse, surah, ayah)
    db_wbw_path = "databases/text/word_by_word_qpc-v2.db"
    words = await run_in_threadpool(get_wbw_text_for_ayah, db_wbw_path, surah, ayah)
    translation = await run_in_threadpool(get_full_translation_for_ayah, surah, ayah, language="bengali")
    surah_obj = await get_surah_by_number(surah)
    surah_name_bangla = surah_obj.bangla_name if surah_obj else f"Surah {surah}"

    # 2. Generate
    gen = ImageGenerator()
    if background_path and os.path.exists(background_path):
        gen.set_background(background_path, dim_opacity=0.4)
    
    y = 200
    h = gen.render_arabic_ayah(words, page_number, font_size=80, y_pos=y)
    y = 500
    h = gen.render_bangla_translation(translation, font_size=45, y_pos=y)
    y = 650
    gen.render_metadata(surah_name_bangla, ayah, font_size=35, y_pos=y)
    gen.render_branding()
    
    img_io = io.BytesIO()
    gen.canvas.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@app.get("/api/generate-image")
async def api_generate_image(
    surah: int, 
    ayah: int, 
    background_path: str = None,
    config: ConfigManager = Depends(get_config_manager)
):
    if not background_path:
        background_path = config.get("ACTIVE_BACKGROUND")
        
    img_io = await _internal_generate_image(surah, ayah, background_path)
    return Response(content=img_io.getvalue(), media_type="image/png")

@app.get("/api/download-image")
async def api_download_image(
    surah: int, 
    ayah: int, 
    background_path: str = None,
    config: ConfigManager = Depends(get_config_manager)
):
    if not background_path:
        background_path = config.get("ACTIVE_BACKGROUND")
        
    img_io = await _internal_generate_image(surah, ayah, background_path)
    return Response(
        content=img_io.getvalue(), 
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=ayah_{surah}_{ayah}.png"}
    )

@app.post("/api/post-image-to-facebook")
async def api_post_image_to_facebook(
    surah: int = Form(...),
    ayah: int = Form(...),
    description: str = Form(...),
    background_path: str = Form(None),
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    # 1. Generate Image
    if not background_path:
        background_path = config.get("ACTIVE_BACKGROUND")
    
    img_io = await _internal_generate_image(surah, ayah, background_path)
    
    # 2. Save temporarily for upload
    temp_dir = "exported_data/temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    import time
    temp_path = os.path.join(temp_dir, f"fb_post_{surah}_{ayah}_{int(time.time())}.png")
    
    with open(temp_path, "wb") as f:
        f.write(img_io.getvalue())
        
    # 3. Get Facebook Credentials for the language
    lang_name = config.get("DEFAULT_LANGUAGE", "bengali")
    stmt = select(Language).where(Language.name == lang_name)
    result = await db.execute(stmt)
    lang_obj = result.scalar_one_or_none()
    
    if not lang_obj or not lang_obj.facebook_page_id or not lang_obj.facebook_access_token:
        return JSONResponse({"status": "error", "message": f"Facebook credentials not configured for language: {lang_name}"}, status_code=400)
        
    # 4. Prepare Caption
    template = config.get("IMAGE_GEN_CAPTION_TEMPLATE", "{user_description}\n\n{surah_name} Ayah {ayah_number}\n\n{hashtags}")
    hashtags = config.get("IMAGE_GEN_DEFAULT_HASHTAGS", "#Quran #TaqwaBangla")
    
    surah_obj = await get_surah_by_number(surah)
    surah_name = surah_obj.bangla_name if surah_obj else f"সূরা {surah}"
    
    caption = template.format(
        user_description=description,
        surah_name=surah_name,
        ayah_number=ayah,
        hashtags=hashtags
    )
    
    # 5. Upload
    from processes.facebook_utils import FacebookClient
    fb = FacebookClient(lang_obj.facebook_access_token, lang_obj.facebook_page_id)
    
    try:
        post_id = await run_in_threadpool(fb.upload_image, temp_path, caption)
        if post_id:
            return {"status": "success", "post_id": post_id}
        else:
            return JSONResponse({"status": "error", "message": "Failed to upload to Facebook. Check logs."}, status_code=500)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

