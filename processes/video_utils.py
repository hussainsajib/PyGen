from moviepy.editor import *
from moviepy.video.fx.resize import resize 



from processes.logger import logger
from processes.Classes.reciter import Reciter
from processes.Classes.surah import Surah
from processes.Classes.verse import Verse
from processes.video_configs import *
from processes.description import generate_details
from processes.backgrounds import crop_image
from factories.video import *
from factories.image import *
from factories.single_clip import *
from factories.composite_clip import *
from factories.file import *



def generate_video(surah_number, start_verse, end_verse, reciter_key, is_short: bool):
    # Prepare background
    background_image_url = fetch_background_image() if not COMMON["is_solid_bg"] else None
    logger.info("Background image downloaded")

    surah = Surah(surah_number)
    reciter = Reciter(tag=reciter_key)
    clips = []
    
    # Conditionally create Intro
    if not is_short and COMMON["enable_intro"]:
        intro = generate_intro(surah, reciter, background_image_url, is_short)
        clips.append(intro)
    
    for verse in range(start_verse, end_verse + 1):
        current_clips = []
        v = Verse(surah=surah, verse=verse, reciter=reciter)
        
        # Skip if any component is missing
        if not (v.arabic and v.link_to_audio and v.translation and (COMMON["is_solid_bg"] or background_image_url)):
            print(f"Skipping verse ${verse} due to missing data.")
            continue
        
        # Download and create the media components
        try:
            audio_clip = AudioFileClip(v.link_to_audio)

            background_clip = generate_background(background_image_url, audio_clip.duration, is_short)
            current_clips.append(background_clip)

            # Create the text overlay
            # Unicode \u06DD is adding the ayah marking at the end
            arabic_text_clip = generate_arabic_text_clip(v.arabic, is_short, audio_clip.duration)
            current_clips.append(arabic_text_clip)

            # Create translation overlay
            
            translation_clip = generate_translation_text_clip(v.translation, is_short, audio_clip.duration)
            current_clips.append(translation_clip)
            logger.info(f"Verse ${verse} TextClip created")

            # Surah name overlay
            if COMMON["enable_footer"]:
                # Reciter name overlay
                if COMMON["enable_reciter_info"]:
                    reciter_name_clip = generate_reciter_name_clip(v.reciter.bangla_name, is_short, audio_clip.duration)
                    current_clips.append(reciter_name_clip)

                if COMMON["enable_surah_info"]:
                    surah_name_clip = generate_surah_info_clip(v.surah.name_bangla, v.verse, is_short, audio_clip.duration)
                    current_clips.append(surah_name_clip)

                # Verser number overlay
                if COMMON["enable_channel_info"]:
                    brand_name_clip = generate_brand_clip("তাকওয়া বাংলা", is_short, audio_clip.duration)
                    current_clips.append(brand_name_clip)

            # Composite the video with text and audio
            video_clip = CompositeVideoClip(current_clips).set_audio(audio_clip)
            logger.info(f"Verse ${verse} CompositeVideoClip created")
            
            clips.append(video_clip)
            
        except Exception as e:
            print(str(e))
            raise
    
    # Check if clips list is empty before concatenation
    if not clips:
        print("No valid clips were generated.")
        return None


    if not is_short and COMMON["enable_outro"]:
        outro = generate_outro(background_image_url, is_short)
        clips.append(outro)

    final_video = concatenate_videoclips(clips)
    output_path = get_filename(surah_number, start_verse, end_verse, reciter.eng_name, is_short)
    
    final_video.write_videofile(output_path, codec='libx264', fps=24, audio_codec="aac")
    
    info_file_path = generate_details(surah, reciter, True, start_verse, end_verse)
    
    return {"video": output_path, "info": info_file_path, "is_short": is_short, "reciter": reciter.tag}
