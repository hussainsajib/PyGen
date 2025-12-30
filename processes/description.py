import os

from bangla import convert_english_digit_to_bangla_digit as e2b

from processes.Classes import Surah, Reciter



def generate_video_title(surah: Surah, reciter: Reciter, has_translation: bool, filename: str, is_short: bool = False, custom_title: str = None, start: int = 1, end: int = 1, language: str = "bengali"):
    title_str = ""
    surah_name = surah.bangla_name if language == "bengali" else surah.english_name
    reciter_name = reciter.bangla_name if language == "bengali" else reciter.english_name
    ayah_start = e2b(str(start)) if language == "bengali" else str(start)
    ayah_end = e2b(str(end)) if language == "bengali" else str(end)
    
    if is_short:
        if custom_title:
            title_str = f"{custom_title} - "
        title_str += f"{surah_name} - {ayah_start}"
        if start != end:
            title_str += f"-{ayah_end}"
        title_str += f" - {reciter_name}"
        
        # Sanitization for YouTube (Simple alphanumeric + space/dash/period)
        import re
        # title_str = re.sub(r'[^a-zA-Z0-9\s\-\.\u0980-\u09FF]', '', title_str) # Keep Bengali
        title_str = title_str[:100]
    else: # Long video title
        if language == "bengali":
            title_str = f"{e2b(str(surah.number))} - {surah_name} - {reciter_name}{' - বাংলা অনুবাদসহ' if has_translation else ''}"
        elif language == "english":
            title_str = f"{surah_name} - {reciter_name}{' - with English Translation' if has_translation else ''}"
    
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{title_str}\n\n")

def generate_video_description(surah: Surah, reciter: Reciter, filename: str, is_short: bool = False, start: int = 1, end: int = 1, language: str = "bengali"):
    with open(filename, "a", encoding="utf-8") as f:
        surah_name = surah.bangla_name if language == "bengali" else surah.english_name
        reciter_name = reciter.bangla_name if language == "bengali" else reciter.english_name
        ayah_start = e2b(str(start)) if language == "bengali" else str(start)
        ayah_end = e2b(str(end)) if language == "bengali" else str(end)

        if language == "bengali":
            if is_short:
                f.write(f"সুরাহ {surah_name} (আয়াত {ayah_start}-{ayah_end})\n")
                f.write(f"তিলাওয়াতঃ {reciter_name}\n\n")
                f.write("কুরআনের এই সুন্দর তিলাওয়াতটি শুনুন এবং শেয়ার করুন। মহান আল্লাহ আমাদের সবাইকে হেদায়েত দান করুন। আমীন।\n\n")
                f.write("Subscribe for more Quran reminders: @TakwaBangla\n")
                f.write("Social Links: facebook.com/TakwaBangla\n\n")
                f.write("#Shorts #Quran #Islam #IslamicReminders #Muslim #TakwaBangla ")
                f.write(f"#Surah{surah.english_name.replace(' ', '')} ") # Keep English surah name for hashtag
            else:
                f.write(f"""{e2b(str(surah.number))} - সুরাহ {surah_name}\nতিলাওয়াতঃ {reciter_name}\n\n""")
            
            f.write("#ইসলামিক_ভিডিও #ইসলাম #ইসলামিক #ইসলামিকভিডিও #কোরান #তিলাওয়াত #quran #qurantilawat #surah #memorize\n\n")
        
        elif language == "english":
            if is_short:
                f.write(f"Surah {surah_name} (Ayat {ayah_start}-{ayah_end})\n")
                f.write(f"Recited by: {reciter_name}\n\n")
                f.write("Listen to this beautiful Quran recitation and share. May Allah guide us all. Ameen.\n\n")
                f.write("Subscribe for more Quran reminders: @Taqwa\n")
                f.write("Social Links: facebook.com/Taqwa\n\n")
                f.write("#Shorts #Quran #Islam #IslamicReminders #Muslim #Taqwa ")
                f.write(f"#Surah{surah_name.replace(' ', '')} ")
            else:
                f.write(f"""Surah {surah_name}\nRecited by: {reciter_name}\n\n""")

            f.write("#IslamicVideo #Islam #Islamic #Quran #Recitation #surah #memorize\n\n")
        
        # Dynamic Tag Generation (added to bottom of info file for reference during upload)
        tags = ["Quran", "Islam", "Islamic", "Quran Tilawat"]
        if language == "bengali":
            tags.extend([reciter_name, surah_name, "Takwa Bangla"])
        else:
            tags.extend([reciter_name, surah_name, "Taqwa"])

        if is_short:
            tags.extend(["Shorts", "YouTube Shorts", "Quran Shorts"])
        
        f.write("TAGS: " + ", ".join(tags))

def generate_details(surah: Surah, reciter: Reciter, has_translation: bool, start: int, end: int, is_short: bool = False, custom_title: str = None, language: str = "bengali") -> str:
    filename = f"exported_data/details/{surah.number}_{start}_{end}_{reciter.english_name.lower().replace(' ', '_')}{'_short' if is_short else ''}.txt"
    if os.path.isfile(filename):
        os.remove(filename)
    generate_video_title(surah, reciter, has_translation, filename, is_short, custom_title, start, end, language)
    generate_video_description(surah, reciter, filename, is_short, start, end, language)
    return filename