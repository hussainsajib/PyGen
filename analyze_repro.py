from PIL import Image
import numpy as np

def analyze_image(filename):
    print(f"--- Analyzing {filename} ---")
    img = Image.open(filename).convert("RGBA")
    arr = np.array(img)
    # Text is white (255,255,255) on black (0,0,0)
    mask = arr[..., 0] > 128 
    
    # Grid parameters from repro script
    height = 1920
    top_margin = height * 0.1 # 192.0
    line_height = (height * 0.8) / 15 # 102.4
    
    slots = [
        ("Surah Header", top_margin, top_margin + line_height),
        ("Bismillah", top_margin + line_height, top_margin + 2 * line_height)
    ]
    
    for name, top, bottom in slots:
        # Crop exactly to the slot area for measurement
        # This prevents picking up neighbor slots
        slot_mask = mask[int(top):int(bottom), :]
        
        coords = np.argwhere(slot_mask)
        if coords.size > 0:
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            
            # These are relative to the top of the slot
            visual_h = y_max - y_min
            visual_center = (y_min + y_max) / 2
            slot_center = (bottom - top) / 2
            
            offset = visual_center - slot_center
            print(f"DEBUG: {name} visual_h={visual_h}, visual_center_in_slot={visual_center:.2f}, slot_center={slot_center:.2f}")
            print(f"{name}: Visual height={visual_h}, Offset={offset:.2f}")
            if abs(offset) < 1.0:
                 print("  Result: Perfectly centered (within 1px)")
            elif offset < 0:
                print(f"  Result: Sitting {abs(offset):.2f} pixels TOO HIGH")
            else:
                print(f"  Result: Sitting {offset:.2f} pixels TOO LOW")
        else:
            print(f"{name}: No content found in slot {top}-{bottom}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            analyze_image(arg)
    else:
        # Fallback to defaults if they exist
        for f in ["repro_surah_1.png", "repro_surah_114.png"]:
             if os.path.exists(f):
                 analyze_image(f)
