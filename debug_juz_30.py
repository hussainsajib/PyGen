import asyncio
from db_ops.crud_mushaf import get_juz_boundaries
from processes.mushaf_video import get_surah_page_range

async def debug_juz_30():
    boundaries = get_juz_boundaries(30)
    print(f"Boundaries: {boundaries}")
    
    surahs = sorted([int(s) for s in boundaries["verse_mapping"].keys()])
    print(f"Surahs in Juz 30: {surahs}")
    
    all_pages = set()
    for s_num in surahs:
        pr = get_surah_page_range(s_num)
        if pr and pr[0]:
            for p in range(pr[0], pr[1] + 1):
                all_pages.add(p)
    
    sorted_pages = sorted(list(all_pages))
    print(f"Pages in Juz 30: {sorted_pages}")

if __name__ == "__main__":
    asyncio.run(debug_juz_30())
