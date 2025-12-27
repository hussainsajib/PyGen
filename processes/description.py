import os

from bangla import convert_english_digit_to_bangla_digit as e2b

from processes.Classes import Surah, Reciter



def generate_video_title(surah: Surah, reciter: Reciter, has_translation: bool, filename: str, is_short: bool = False, custom_title: str = None, start: int = 1, end: int = 1):
    title_str = ""
    if is_short:
        if custom_title:
            title_str = f"{custom_title} - "
        title_str += f"{surah.name_bangla} - {e2b(str(start))}"
        if start != end:
            title_str += f"-{e2b(str(end))}"
        title_str += f" - {reciter.bangla_name}"
        
        # Sanitization for YouTube (Simple alphanumeric + space/dash/period)
        import re
        # title_str = re.sub(r'[^a-zA-Z0-9\s\-\.\u0980-\u09FF]', '', title_str) # Keep Bengali
        title_str = title_str[:100]
    else:
        title_str = f"{e2b(str(surah.number))} - সুরাহ {surah.name_bangla} - {reciter.bangla_name}{' - বাংলা অনুবাদসহ' if has_translation else ''}"
    
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{title_str}\n\n")

def generate_video_description(surah: Surah, reciter: Reciter, filename: str, is_short: bool = False, start: int = 1, end: int = 1):
    with open(filename, "a", encoding="utf-8") as f:
        if is_short:
            f.write(f"সুরাহ {surah.name_bangla} (আয়াত {e2b(str(start))}-{e2b(str(end))})\n")
            f.write(f"তিলাওয়াতঃ {reciter.bangla_name}\n\n")
            f.write("কুরআনের এই সুন্দর তিলাওয়াতটি শুনুন এবং শেয়ার করুন। মহান আল্লাহ আমাদের সবাইকে হেদায়েত দান করুন। আমীন।\n\n")
            f.write("Subscribe for more Quran reminders: @TakwaBangla\n")
            f.write("Social Links: facebook.com/TakwaBangla\n\n")
            f.write("#Shorts #Quran #Islam #IslamicReminders #Muslim #TakwaBangla ")
            # Add surah specific hashtag
            f.write(f"#Surah{surah.eng_name.replace(' ', '')} ")
        else:
            f.write(f"""{e2b(str(surah.number))} - সুরাহ {surah.name_bangla}\nতিলাওয়াতঃ {reciter.bangla_name}\n\n""")
        
        f.write("#ইসলামিক_ভিডিও #ইসলাম #ইসলামিক #ইসলামিকভিডিও #কোরান #তিলাওয়াত #quran #qurantilawat #surah #memorize\n\n")
        
        # Dynamic Tag Generation (added to bottom of info file for reference during upload)
        tags = ["Quran", "Islam", "Islamic", "Quran Tilawat", reciter.eng_name, surah.eng_name, "Takwa Bangla"]
        if is_short:
            tags.extend(["Shorts", "YouTube Shorts", "Quran Shorts"])
        
        f.write("TAGS: " + ", ".join(tags))

def generate_details(surah: Surah, reciter: Reciter, has_translation: bool, start: int, end: int, is_short: bool = False, custom_title: str = None) -> str:
    filename = f"exported_data/details/{surah.number}_{start}_{end}_{reciter.eng_name.lower().replace(' ', '_')}{'_short' if is_short else ''}.txt"
    if os.path.isfile(filename):
        os.remove(filename)
    generate_video_title(surah, reciter, has_translation, filename, is_short, custom_title, start, end)
    generate_video_description(surah, reciter, filename, is_short, start, end)
    return filename