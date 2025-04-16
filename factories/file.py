

def get_filename(surah: int, start: int, end: int, reciter: str, is_short: bool):
    b_filename = f"{surah}_{start}_{end}_{reciter.lower().replace(' ', '_')}.mp4"
    if is_short:
        return f"exported_data/shorts/quran_shorts_{b_filename}"
    return f"exported_data/videos/quran_video_{b_filename}"