import os
import platform
import logging

logger = logging.getLogger(__name__)

def resolve_font_path(font_name: str) -> str:
    """
    Robustly resolves a font name or filename to an absolute disk path.
    Checks:
    1. Local 'fonts/' directory.
    2. System-specific font directories (Windows, Linux, macOS).
    3. Returns the original name if not found (MoviePy fallback).
    """
    if not font_name:
        return "Arial"

    # Normalize name
    base_name = font_name
    if not base_name.lower().endswith(".ttf"):
        base_name += ".ttf"

    # 1. Check local project directory
    local_path = os.path.abspath(os.path.join("fonts", base_name))
    if os.path.exists(local_path):
        return local_path

    # 2. Check system font directories
    system = platform.system()
    potential_dirs = []

    if system == "Windows":
        windir = os.environ.get("WINDIR", "C:\Windows")
        potential_dirs.append(os.path.join(windir, "Fonts"))
    elif system == "Darwin": # macOS
        potential_dirs.extend([
            os.path.expanduser("~/Library/Fonts"),
            "/Library/Fonts",
            "/System/Library/Fonts"
        ])
    else: # Linux/POSIX
        potential_dirs.extend([
            os.path.expanduser("~/.local/share/fonts"),
            "/usr/share/fonts",
            "/usr/local/share/fonts"
        ])

    for d in potential_dirs:
        if not os.path.exists(d):
            continue
        
        # Search recursively for the font file
        for root, _, files in os.walk(d):
            if base_name.lower() in [f.lower() for f in files]:
                # Find the exact case-sensitive match if possible
                for f in files:
                    if f.lower() == base_name.lower():
                        return os.path.join(root, f)

    logger.warning(f"Could not resolve font path for '{font_name}'. Using fallback.")
    return font_name
