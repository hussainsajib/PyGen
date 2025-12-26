import os
import json
import asyncio
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Request, Depends, Form, Header, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
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
    enqueue_manual_upload_job
)

from db_ops import crud_reciters
from config_manager import ConfigManager, config_manager, get_config_manager
from processes.youtube_utils import (
    get_authenticated_service,
    get_all_playlists,
    get_videos_from_playlist,
    update_video_privacy,
)

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

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
templates = Jinja2Templates(directory="templates")



from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/create-video")
async def create_video(
    request: Request, 
    background_tasks: BackgroundTasks, 
    surah: int, 
    start_verse: int, 
    end_verse: int, 
    reciter: str,
    is_short: bool = False
):
    background_tasks.add_task(create_and_post, surah, start_verse, end_verse, reciter, is_short)
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
                 db: AsyncSession = Depends(get_db)
    ):
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        surah_name = data[str(surah_number)]["english_name"]
    await enqueue_job(db, surah_number, surah_name=surah_name, reciter=reciter)
    #background_tasks.add_task(create_surah_video, surah_number, reciter)
    return RedirectResponse(request.url_for("surah"))

@app.get("/create-all-surah-videos", name="create_all_surah_videos")
async def create_all_surah_videos(request: Request, reciter: str, db: AsyncSession = Depends(get_db)):
    with open("data/surah_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
        for surah_number in range(1, 115):
            surah_name = data[str(surah_number)]["english_name"]
            print(f"Enqueuing job for Surah {surah_number}: {surah_name} with reciter {reciter}")
            await enqueue_job(db, surah_number, surah_name=surah_name, reciter=reciter)
    
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
    config: ConfigManager = Depends(get_config_manager)
):
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
    
    return templates.TemplateResponse("config.html", {
        "request": request, 
        "config": config_items,
        "reciters": reciters
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


from net_ops.unsplash import search_unsplash, download_unsplash_image

@app.get("/unsplash-search")
async def unsplash_search(query: str):
    results = await run_in_threadpool(search_unsplash, query)
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
    await config.delete(db, "ACTIVE_BACKGROUND")
    return {"status": "success"}

@app.post("/download-unsplash")
async def download_unsplash(
    url: str = Form(...),
    filename: str = Form(...),
    db: AsyncSession = Depends(get_db),
    config: ConfigManager = Depends(get_config_manager)
):
    path = await run_in_threadpool(download_unsplash_image, url, filename)
    if path:
        await config.set(db, "ACTIVE_BACKGROUND", path)
        return {"status": "success", "path": path}
    return {"status": "error", "message": "Download failed"}


@app.get("/reciters", name="reciters_list", response_class=HTMLResponse)
async def get_reciters_page(request: Request, db: AsyncSession = Depends(get_db)):
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
    await crud_reciters.create_reciter(db, dict(form_data))
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
    await crud_reciters.update_reciter(db, reciter_id, dict(form_data))
    return RedirectResponse(url=request.url_for("reciters_list"), status_code=303)

@app.post("/reciter/{reciter_id}/delete", name="reciter_delete")
async def reciter_delete(request: Request, reciter_id: int, db: AsyncSession = Depends(get_db)):
    await crud_reciters.delete_reciter(db, reciter_id)
    return RedirectResponse(url=request.url_for("reciters_list"), status_code=303)


def validate_wbw_exists(filename: str):
    if not filename:
        return True # Optional field
    return os.path.exists(os.path.join("databases", "word-by-word", filename))
