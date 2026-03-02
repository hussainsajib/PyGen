# PyGen - Islamic Multimedia Generator

PyGen is a high-performance Python-based application built with **FastAPI** designed to automate the generation of Islamic multimedia content. It creates Quranic videos and social media images that combine authentic Arabic calligraphy (**QPC v2 fonts**) with translations (primarily **Bangla**), synchronized recitations, and customizable backgrounds.

### Key Features
- **Video Generation:** Combines Quranic recitations, translations, and customizable visual elements (Standard, WBW, and Mushaf styles).
- **Image Post Generator:** Creates 1:1 square, portrait, or landscape images for social media with authentic calligraphy.
- **Job Management:** robust queuing system for managing long-running generation tasks.
- **Social Integration:** Automatic posting to Facebook (Videos/Photos) and YouTube (Videos/Shorts).
- **Web Interface:** User-friendly dashboard for selection, configuration, and asset management.

## Technical Stack
- **Backend:** Python, FastAPI, SQLAlchemy (PostgreSQL), Uvicorn.
- **Media Processing:** Pillow (Images), MoviePy & FFmpeg (Video), uharfbuzz & freetype (Complex text shaping).
- **APIs:** Facebook Graph, YouTube Data v3, Unsplash, Pexels.

## Getting Started

### Environment Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file with `DATABASE_URL` and API keys.

### Running the App
```bash
uvicorn app:app --reload
```
The application will automatically initialize the database schema on startup.

## Architecture
- `app.py`: Main FastAPI application and routing.
- `factories/`: Core rendering engines for multimedia.
- `processes/`: Background workers and third-party integrations.
- `db_ops/`: Logic-specific CRUD operations.
- `conductor/`: Development workflow artifacts (Specs/Plans).
- `tools_to_analyze_debug/`: Centralized analysis and debugging scripts.

## Background Color - Font Color Combinations
- Background: rgb(35, 61, 77); font: rgb(254, 127, 45)
- Background: rgb(197, 216, 109); font: rgb(78, 135, 140)
- Background: rgb(37, 89, 87); font: rgb(247, 197, 72)
- Background: rgb(249, 235, 224); font: rgb(32, 138, 174)
