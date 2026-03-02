# GEMINI instructional context for PyGen

## Project Overview
PyGen is a high-performance Python-based application built with **FastAPI** designed to automate the generation of Islamic multimedia content. It specializes in creating Quranic videos and social media images that combine authentic Arabic calligraphy (**QPC v2 fonts**) with translations (primarily **Bangla**), synchronized recitations, and customizable backgrounds.

### Main Technologies
- **Backend:** Python, FastAPI, SQLAlchemy (PostgreSQL/asyncpg), Uvicorn.
- **Media Processing:** Pillow (Image generation), MoviePy (Video composition), FFmpeg (Rendering), OpenCV/PyAV (High-speed engines).
- **APIs:** Facebook Graph API, YouTube Data API v3, Unsplash API, Pexels API.
- **Frontend:** Jinja2 Templates, Bootstrap 5, FontAwesome.
- **Development Framework:** Conductor (Spec-driven development workflow).

## Architecture & Directory Structure
- `app.py`: Main FastAPI application, route definitions, and lifecycle management.
- `db_ops/`: Logic-specific CRUD operations (Surah, Text, Jobs, Media Assets).
- `factories/`: Core rendering engines for videos (`mushaf_ffmpeg_engine.py`) and images (`image_generator.py`).
- `processes/`: Business logic, background workers, and external service integrations (YouTube/Facebook).
- `db/`: Database configuration, models (SQLAlchemy), and migrations.
- `conductor/`: Instructional context, track specifications, and implementation plans.
- `tools_to_analyze_debug/`: Centralized folder for all analysis, debugging, and reproduction scripts.
- `exported_data/`: Output directory for generated videos, shorts, and screenshots.

## Building and Running
- **Environment Setup:** 
  ```bash
  pip install -r requirements.txt
  ```
- **Database Initialization:** 
  The application automatically initializes the database schema via the `lifespan` event in `app.py`. Ensure `DATABASE_URL` is set in `.env`.
- **Running the Application:**
  ```bash
  uvicorn app:app --reload
  ```
- **Configuration:**
  Settings are managed via the web UI (`/config`) and stored in the database. Key environment variables (tokens, API keys) must be provided in a `.env` file.

## Development Conventions
1. **Conductor Workflow:** 
   Always operate within the Conductor framework. New features or fixes must start with a Track in `conductor/tracks/`, involving a `spec.md` and `plan.md`.
2. **Testing (TDD):** 
   Tests should be created in the `tests/` directory. For feature verification, utilize `pytest`.
3. **Clean Root Protocol:** 
   Do not clutter the project root with temporary scripts. Use `tools_to_analyze_debug/` for any files related to analysis, debugging, or reproduction.
4. **Typography & Shaping:** 
   - Use **QPC v2** fonts for Arabic (stored in `QPC_V2_Font.ttf/`).
   - Use **manual shaping** (via `factories/shaping_utils.py`) for complex scripts like Bangla to ensure correct glyph rendering.
5. **Localization:** 
   Prioritize Bengali localization. Numbers in metadata should be converted using the `bangla` library (`e2b` utility).
6. **Git Standards:**
   Follow the project's commit message conventions (e.g., `feat(module): ...`, `fix(module): ...`, `chore(conductor): ...`).
