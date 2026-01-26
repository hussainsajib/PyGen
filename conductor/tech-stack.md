# PyGen Technology Stack

## Core Language & Runtime
- **Language:** Python
- **Backend Framework:** FastAPI (High-performance, asynchronous web framework)
- **ASGI Server:** Uvicorn

## Data Management
- **Primary Database:** PostgreSQL (Advanced relational database)
- **ORM/Database Toolkit:** SQLAlchemy (Using `asyncpg` for asynchronous PostgreSQL access)
- **Word-by-Word Databases:** SQLite (Local storage for synchronized word-level timestamps, Arabic text, and translations)
- **Mushaf Structural Data:** Specialized SQLite databases (`qpc-v2-15-lines.db`) defining precise page/line/word boundaries for authentic rendering.
- **High-Fidelity Typography:** Support for Private Use Area (PUA) glyphs and page-specific TrueType fonts (QPC v2) for perfect Mushaf representation.
- **Secondary Storage:** TinyDB (Used for lightweight, document-based storage where applicable)

## Media Processing
- **Video Composition:** MoviePy (Script-based video editing)
- **Resource Management:** Dynamic CPU-aware threading for optimized video encoding.
- **Computer Vision:** OpenCV (Used for image manipulation and analysis)
- **Image Processing:** Pillow (PIL Fork - Comprehensive image library)

## Frontend & Templating
- **Frontend Framework:** React (Integrated with FastAPI for dynamic user interfaces)
- **CSS Framework:** Bootstrap 5 (Used for responsive grid systems and consistent UI styling)
- **Templating Engine:** Jinja2 (Integrated with FastAPI for server-side rendering and dynamic font-face injection)
- **Static Assets:** CSS/JavaScript for modern, bold UI components

## Integrations & APIs
- **Google Cloud Platform:** 
    - YouTube Data API v3 (For automated uploads and playlist management)
    - Google Auth/OAuth 2.0 (For secure API authorization)
    - Google Cloud Storage (For media asset persistence)
- **Meta for Developers:**
    - Facebook Graph API v19.0 (For automated Page video and Reels uploads)
    - Long-lived Page Access Tokens (For persistent server-side authorization)
- **Unsplash API:** For searching and downloading high-quality stock images for video backgrounds.
- **Pexels API:** For searching and downloading high-quality stock videos for video backgrounds.
