from db_ops.crud_surah import read_surah_data, read_timestamp_data
from db_ops.crud_text import read_text_data, read_translation
from net_ops.download_file import download_mp3_temp, cleanup_temp_file

from moviepy.editor import *
import tempfile
import json

screen_size = (1280, 720)  # Set the screen size for the video clips


def create_ayah_clip(surah, ayah, gstart_ms, gend_ms, segments_string, surah_data, translation_data, full_audio):
    # Calculate the ayah duration in seconds
    duration = (gend_ms - gstart_ms) / 1000.0
    
    # Get the words for the ayah and build the full ayah text
    words_dict = surah_data.get(surah, {}).get(ayah, {})
    if not words_dict:
        raise ValueError(f"No data for surah {surah} ayah {ayah}")

    # Order words by their keys (word numbers)
    sorted_word_nums = sorted(words_dict.keys())
    full_ayah_text = " ".join(words_dict[w] for w in sorted_word_nums)
    
    # Create a base clip with the full ayah text (non-highlighted)
    base_clip = (TextClip(full_ayah_text,
                          fontsize=60,
                          font='Amiri-Bold',
                          color='white',
                          size=screen_size,
                          method='caption')
                 .set_position('center')
                 .set_duration(duration))

    translation_text = translation_data[(surah, ayah)]
    trans_clip = (TextClip(translation_text,
                        fontsize=40,
                        font='Kalpurush',
                        color='lightblue',
                        method='caption',
                        size=(screen_size[0] - 100, None))  # Optional: adjust width to fit within screen
                .set_position(("center", "bottom"))
                .set_duration(duration))
    
    # Parse the segments string safely. Here we use json.loads instead of eval,
    # so the segments should be a proper JSON string. Adjust if needed.
    try:
        segments = json.loads(segments_string)
    except Exception as e:
        print("Error parsing segments string:", segments_string)
        segments = []
    
    # highlight_clips = []
    # # For each segment, create an overlay clip that highlights the corresponding word.
    # # We simply display that word in a larger font and a different color.
    # for seg in segments:
    #     # Each segment is expected to be a list like [word_index, seg_start, seg_end].
    #     # If the segment doesn't have three items, skip it.
    #     if not (isinstance(seg, list) and len(seg) >= 3):
    #         continue
    #     word_index, seg_start, seg_end = seg[:3]
    #     seg_duration = (seg_end - seg_start) / 1000.0
        
    #     # Get the word text from surah_data
    #     highlighted_word = words_dict.get(word_index, '')
    #     if not highlighted_word:
    #         continue
        
    #     # Create a highlighted text clip for that word.
    #     # (You can adjust fontsize, color, and position as needed.)
    #     h_clip = (TextClip(highlighted_word,
    #                        fontsize=80,
    #                        font='Amiri-Bold',
    #                        color='yellow',
    #                        method='caption')
    #               .set_position('center')
    #               .set_duration(seg_duration)
    #               .set_start(seg_start / 1000.0))
    #     highlight_clips.append(h_clip)
    
    # Composite the base clip and highlight clips together.
    composite = CompositeVideoClip([base_clip, trans_clip], size=screen_size).set_duration(duration)
    
    # Subclip the audio for the ayah (convert global ms to seconds)
    ayah_audio = full_audio.subclip(gstart_ms / 1000.0, gend_ms / 1000.0)
    composite = composite.set_audio(ayah_audio)
    
    return composite


def generate_surah(surah_number: int):
    surah_url = read_surah_data(surah_number)
    downloaded_surah_file = download_mp3_temp(surah_url)
    full_audio = AudioFileClip(downloaded_surah_file)
    #print(f"Downloaded Surah file: {downloaded_surah_file}")
    surah_data = read_text_data(surah_number)
    translation_data = read_translation(surah_number)
    timestamp_data = read_timestamp_data(surah_number)
    ayah_clips = []
    for tdata in timestamp_data:
        surah, ayah, gstart_ms, gend_ms, seg_str = tdata
        clip = create_ayah_clip(surah, ayah, gstart_ms, gend_ms, seg_str, surah_data, translation_data, full_audio)
        ayah_clips.append(clip)

    # Concatenate all ayah clips one after the other
    final_video = concatenate_videoclips(ayah_clips)

    # Write the final video to a temporary file.
    output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    final_video.write_videofile(output_path, fps=24)
    
    