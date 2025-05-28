from moviepy.editor import CompositeVideoClip, AudioFileClip, TextClip

from factories.single_clip import generate_background
from processes.video_configs import FONT_COLOR, COMMON
from processes.Classes import Reciter, Surah

def generate_intro(surah: Surah, reciter: Reciter, background_image_url, is_short: bool):
    intro_clips = []
    audio = AudioFileClip("recitation_data/basmalah.mp3")
    background = generate_background(background_image_url, audio.duration, is_short)
    intro_clips.append(background)

    if COMMON["enable_title"]:
        title = TextClip(txt=f"সুরাহ {surah.name_bangla}", font="kalpurush", fontsize=100, color=FONT_COLOR)\
            .set_position(("center", 0.4), relative=True)\
            .set_duration(audio.duration)
        intro_clips.append(title)

    if COMMON["enable_subtitle"]:
        sub_title = TextClip(txt=f"{reciter.bangla_name}", font="kalpurush", fontsize=50, color=FONT_COLOR)\
                .set_position(("center", 0.6), relative=True)\
                .set_duration(audio.duration)
        intro_clips.append(sub_title)
    composite_clip = CompositeVideoClip(intro_clips)
    if surah.number == 9:
        return composite_clip
    return composite_clip.set_audio(audio)

def generate_outro(background_image_url, is_short):
    background = generate_background(background_image_url, duration=5, is_short=is_short)
    title = TextClip("তাকওয়া বাংলা", font="kalpurush", fontsize=70, color=FONT_COLOR)\
            .set_position(('center', 'center'))\
            .set_duration(5)
    return CompositeVideoClip([background, title])