import os
from PIL import Image
from factories.wbw_fast_render import WBWFastRenderer

def verify_standard():
    scene_data = {
        "words": ["اللَّهُ", "نُورُ", "السَّمَاوَاتِ"],
        "translations": ["Allah", "is the Light", "of the heavens"],
        "start_ms": 0,
        "end_ms": 3000,
        "word_segments": [
            {"start_ms": 0, "end_ms": 1000},
            {"start_ms": 1000, "end_ms": 2000},
            {"start_ms": 2000, "end_ms": 3000}
        ],
        "reciter_name": "Mishary Alafasy",
        "surah_name": "An-Nur",
        "verse_number": 35,
        "brand_name": "Taqwa",
        "is_short": False,
        "layout": "standard"
    }
    
    output_dir = "phase2_verification/standard"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    renderer = WBWFastRenderer(scene_data)
    
    for i, ts in enumerate([0.5, 1.5, 2.5]):
        frame = renderer.get_frame_at(ts)
        Image.fromarray(frame).save(os.path.join(output_dir, f"standard_highlight_{i+1}.png"))
    print(f"Standard layout frames saved to {output_dir}")

def verify_interlinear():
    scene_data = {
        "words": ["اللَّهُ", "نُورُ", "السَّمَاوَاتِ"],
        "translations": ["Allah", "Light", "Heavens"],
        "start_ms": 0,
        "end_ms": 3000,
        "word_segments": [
            {"start_ms": 0, "end_ms": 1000},
            {"start_ms": 1000, "end_ms": 2000},
            {"start_ms": 2000, "end_ms": 3000}
        ],
        "reciter_name": "Mishary Alafasy",
        "surah_name": "An-Nur",
        "verse_number": 35,
        "brand_name": "Taqwa",
        "is_short": False,
        "layout": "interlinear"
    }
    
    output_dir = "phase2_verification/interlinear"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    renderer = WBWFastRenderer(scene_data)
    
    for i, ts in enumerate([0.5, 1.5, 2.5]):
        frame = renderer.get_frame_at(ts)
        Image.fromarray(frame).save(os.path.join(output_dir, f"interlinear_highlight_{i+1}.png"))
    print(f"Interlinear layout frames saved to {output_dir}")

if __name__ == "__main__":
    verify_standard()
    verify_interlinear()
