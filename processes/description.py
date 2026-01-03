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