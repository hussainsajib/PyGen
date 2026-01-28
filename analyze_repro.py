from PIL import Image
import numpy as np

def analyze_image(filename):
    print(f"--- Analyzing {filename} ---")
    img = Image.open(filename).convert("RGBA")
    arr = np.array(img)
    alpha = arr[..., 3]
    
    # Grid parameters from repro script
    # width, height = (1080, 1920) for is_short=True
    # top_margin = height * 0.1 = 192
    # usable_height = height * 0.8 = 1536
    # line_height = 1536 / 15 = 102.4
    
    # Surah Header is line 0: y_pos = 192
    # Bismillah is line 1: y_pos = 192 + 102.4 = 294.4
    
    line_height = 102.4
    slots = [
        ("Surah Header", 192, 192 + 102.4),
        ("Bismillah", 294.4, 294.4 + 102.4)
    ]
    
    for name, top, bottom in slots:
        # Crop the slot
        slot_alpha = alpha[int(top):int(bottom), :]
        coords = np.argwhere(slot_alpha > 0)
        if coords.size > 0:
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            
            # These are relative to the top of the slot
            actual_top = y_min
            actual_bottom = y_max
            visual_h = actual_bottom - actual_top
            
            # Center of the ink relative to slot
            visual_center = (actual_top + actual_bottom) / 2
            slot_center = (bottom - top) / 2
            
            offset = visual_center - slot_center
            print(f"{name}: Visual height={visual_h}, Visual center={visual_center:.2f}, Slot center={slot_center:.2f}, Offset={offset:.2f}")
            if offset < 0:
                print(f"  Result: Sitting {abs(offset):.2f} pixels TOO HIGH")
            elif offset > 0:
                print(f"  Result: Sitting {offset:.2f} pixels TOO LOW")
            else:
                print("  Result: Perfectly centered")
        else:
            print(f"{name}: No content found")

if __name__ == "__main__":
    analyze_image("repro_surah_1.png")
    analyze_image("repro_surah_114.png")
