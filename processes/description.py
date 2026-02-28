import os

from bangla import convert_english_digit_to_bangla_digit as e2b

from processes.Classes import Surah, Reciter



def get_title_string(surah: Surah, reciter: Reciter, has_translation: bool, is_short: bool = False, custom_title: str = None, start: int = 1, end: int = 1, language: str = "bengali"):
    surah_name = surah.bangla_name if language == "bengali" else surah.english_name
    reciter_name = reciter.bangla_name if language == "bengali" else reciter.english_name
    
    surah_prefix = "সুরাহ" if language == "bengali" else "Surah"
    surah_num = e2b(str(surah.number)) if language == "bengali" else str(surah.number)
    
    ayah_start = e2b(str(start)) if language == "bengali" else str(start)
    ayah_end = e2b(str(end)) if language == "bengali" else str(end)
    
    ayah_range = f"({ayah_start})" if start == end else f"({ayah_start}-{ayah_end})"
    
    title_str = f"{surah_num}. {surah_prefix} {surah_name} {ayah_range} - {reciter_name}"
    
    if is_short and custom_title:
        title_str = f"{custom_title} - {title_str}"
    
    if not is_short:
        if language == "bengali" and has_translation:
            title_str += " - বাংলা অনুবাদসহ"
        elif language == "english" and has_translation:
            title_str += " - with English Translation"

    return title_str[:100]

def generate_video_title(surah: Surah, reciter: Reciter, has_translation: bool, filename: str, is_short: bool = False, custom_title: str = None, start: int = 1, end: int = 1, language: str = "bengali"):
    title_str = get_title_string(surah, reciter, has_translation, is_short, custom_title, start, end, language)
    
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{title_str}\n\n")

def generate_video_description(surah: Surah, reciter: Reciter, filename: str, is_short: bool = False, start: int = 1, end: int = 1, language: str = "bengali"):
    title_header = get_title_string(surah, reciter, False, is_short, None, start, end, language)
    
    with open(filename, "a", encoding="utf-8") as f:
        surah_name = surah.bangla_name if language == "bengali" else surah.english_name
        reciter_name = reciter.bangla_name if language == "bengali" else reciter.english_name
        
        f.write(f"{title_header}\n\n")

        if language == "bengali":
            f.write("কুরআনের এই সুন্দর তিলাওয়াতটি শুনুন এবং শেয়ার করুন। মহান আল্লাহ আমাদের সবাইকে হেদায়েত দান করুন। আমীন।\n\n")
            f.write("Subscribe for more Quran reminders: @TaqwaBangla\n")
            f.write("Social Links: https://www.facebook.com/profile.php?id=61570927757129\n\n")
            
            f.write("#Shorts #Quran #Islam #IslamicReminders #Muslim #TaqwaBangla ")
            f.write(f"#Surah{surah.english_name.replace(' ', '')} ")
            f.write("#ইসলামিক_ভিডিও #ইসলাম #ইসলামিক #ইসলামিকভিডিও #কোরান #তিলাওয়াত #quran #qurantilawat #surah #memorize\n\n")
        
        elif language == "english":
            f.write("Listen to this beautiful Quran recitation and share. May Allah guide us all. Ameen.\n\n")
            f.write("Subscribe for more Quran reminders: @TaqwaBangla\n")
            f.write("Social Links: https://www.facebook.com/profile.php?id=61570927757129\n\n")
            
            f.write("#Shorts #Quran #Islam #IslamicReminders #Muslim #TaqwaBangla ")
            f.write(f"#Surah{surah.english_name.replace(' ', '')} ")
            f.write("#IslamicVideo #Islam #Islamic #Quran #Recitation #surah #memorize\n\n")
        
        # Dynamic Tag Generation
        tags = ["Quran", "Islam", "Islamic", "Quran Tilawat", "Taqwa Bangla"]
        tags.extend([reciter_name, surah_name])
        
        if is_short:
            tags.extend(["Shorts", "YouTube Shorts", "Quran Shorts"])
        
        # Add surah name and reciter name again as per prompt if needed
        # tags.extend([surah_name, reciter_name])

        f.write("TAGS: " + ", ".join(tags))

def generate_details(surah: Surah, reciter: Reciter, has_translation: bool, start: int, end: int, is_short: bool = False, custom_title: str = None, language: str = "bengali") -> str:

    filename = f"exported_data/details/{surah.number}_{start}_{end}_{reciter.english_name.lower().replace(' ', '_')}{'_short' if is_short else ''}.txt"

    if os.path.isfile(filename):

        os.remove(filename)

    generate_video_title(surah, reciter, has_translation, filename, is_short, custom_title, start, end, language)

    generate_video_description(surah, reciter, filename, is_short, start, end, language)

    return filename



def seconds_to_hms(seconds: float) -> str:

    """Formats seconds into HH:MM:SS or MM:SS."""

    h = int(seconds // 3600)

    m = int((seconds % 3600) // 60)

    s = int(seconds % 60)

    if h > 0:

        return f"{h:02d}:{m:02d}:{s:02d}"

    return f"{m:02d}:{s:02d}"



def generate_juz_details(juz_number: int, reciter: Reciter, offsets: dict, is_short: bool = False, language: str = "bengali", custom_title: str = None) -> str:
    """
    Generates localized title and description for a Juz video, including chapter markers.
    """
    filename = f"exported_data/details/juz_{juz_number}_{reciter.english_name.lower().replace(' ', '_')}{'_short' if is_short else ''}.txt"
    if os.path.isfile(filename):
        os.remove(filename)
        
    reciter_name = reciter.bangla_name if language == "bengali" else reciter.english_name
    
    # Labels
    juz_label = "পারা" if language == "bengali" else "Juz"
    quran_recitation_label = "কুরআন তিলাওয়াত" if language == "bengali" else "Quran Recitation"
    surah_label = "সুরাহ" if language == "bengali" else "Surah"
    
    juz_num_str = e2b(str(juz_number)) if language == "bengali" else str(juz_number)
    
    # 1. Title: [Localized Juz] [Num] - [Reciter] - [Localized Quran Recitation]
    title = f"{juz_label} {juz_num_str} - {reciter_name} - {quran_recitation_label}"
    
    if is_short and custom_title:
        title = f"{custom_title} - {title}"
        
    # 2. Description
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{title}\n\n")
        
        if language == "bengali":
            f.write(f"সম্পূর্ণ {juz_label} {juz_num_str} তিলাওয়াত। কুরআনের এই সুন্দর তিলাওয়াতটি শুনুন এবং শেয়ার করুন।\n\n")
        else:
            f.write(f"Full {juz_label} {juz_number} Recitation. Listen to this beautiful Quran recitation and share.\n\n")
            
        # Chapter Markers
        f.write("Chapters:\n")
        # Sort surahs in the Juz by their start offset
        sorted_surahs = sorted(offsets.items(), key=lambda x: x[1])
        
        for i, (surah_num, offset_ms) in enumerate(sorted_surahs):
            # Force the first Surah to start at 00:00 to satisfy YouTube's requirements
            # and include the intro silence in the first chapter.
            if i == 0:
                offset_sec = 0.0
            else:
                offset_sec = float(offset_ms) / 1000.0
                
            s_obj = Surah(surah_num)
            s_name = s_obj.bangla_name if language == "bengali" else s_obj.english_name
            f.write(f"{seconds_to_hms(offset_sec)} {surah_label} {s_name}\n")
        f.write("\n")
        
        f.write("Subscribe for more Quran reminders: @TaqwaBangla\n")
        f.write("Social Links: https://www.facebook.com/profile.php?id=61570927757129\n\n")
        
        if language == "bengali":
            f.write(f"#{juz_label.replace(' ', '')}{juz_number} #Full{juz_label.replace(' ', '')} #Quran #Recitation #TaqwaBangla #Islam\n\n")
        else:
            f.write(f"#Juz{juz_number} #FullJuz #Quran #Recitation #TaqwaBangla #Islam\n\n")
        
        # Tags
        if language == "bengali":
            tags = ["Quran", "Islam", "Islamic", "Quran Tilawat", "Taqwa Bangla", reciter_name, f"{juz_label} {juz_num_str}"]
        else:
            tags = ["Quran", "Islam", "Islamic", "Quran Tilawat", "Taqwa Bangla", reciter_name, f"Juz {juz_number}"]
        f.write("TAGS: " + ", ".join(tags))
        
    return filename
