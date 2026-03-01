import os
from PIL import Image
from factories.wbw_fast_render import WBWFastRenderer

def verify():
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
        "is_short": False
    }
    
    output_dir = "phase1_verification"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    renderer = WBWFastRenderer(scene_data)
    
    # Save base frame (no highlight)
    base_frame = renderer.get_frame_at(-1.0)
    Image.fromarray(base_frame).save(os.path.join(output_dir, "base_frame.png"))
    
    # Save frames with highlights for each word
    for i, ts in enumerate([0.5, 1.5, 2.5]):
        frame = renderer.get_frame_at(ts)
        Image.fromarray(frame).save(os.path.join(output_dir, f"highlight_word_{i+1}.png"))
        
    print(f"Verification frames saved to {output_dir}")

if __name__ == "__main__":
    verify()
