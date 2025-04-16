import os

from bangla import convert_english_digit_to_bangla_digit as e2b

from processes.Classes import Surah, Reciter, Verse



def generate_video_title(surah: Surah, reciter: Reciter, has_translation: bool, filename: str):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{e2b(str(surah.number))} - সুরাহ {surah.name_bangla} - {reciter.bangla_name}{" - বাংলা অনুবাদসহ" if has_translation else None}\n\n")

def generate_video_description(surah: Surah, reciter: Reciter, filename: str):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"""{e2b(str(surah.number))} - সুরাহ {surah.name_bangla}\nতিলাওয়াতঃ {reciter.bangla_name}\n\n""")
        f.write("#ইসলামিক_ভিডিও #ইসলাম #ইসলামিক#ইসলামিক_ভিডিও #ইসলামিকভিডিও #ইসলামিক #ইসলাম #ইসলামিক_ভিডিও #কোরান #তিলাওয়াত #quran #qurantilawat #surah #memorize")

def generate_details(surah: Surah, reciter: Reciter, has_translation: bool, start: int, end: int) -> str:
    filename = f"exported_data/details/{surah.number}_{start}_{end}_{reciter.eng_name.lower().replace(" ", "_")}.txt"
    if os.path.isfile(filename):
        os.remove(filename)
    generate_video_title(surah, reciter, has_translation, filename)
    generate_video_description(surah, reciter, filename)
    return filename