from PIL import Image
import numpy as np
import os

def analyze_image(filename):
    print(f"--- Analyzing {filename} ---")
    img = Image.open(filename).convert("RGB")
    arr = np.array(img)
    
    # Target font color: rgb(201, 181, 156)
    target_color = (201, 181, 156)
    
    # Allow some tolerance due to anti-aliasing
    diff = np.abs(arr - target_color)
    mask = np.all(diff < 5, axis=-1)
    
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
        slot_mask = mask[int(top):int(bottom), :]
        
        coords = np.argwhere(slot_mask)
        if coords.size > 0:
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            
            # These are relative to the top of the slot
            visual_h = y_max - y_min
            visual_center_y = (y_min + y_max) / 2
            slot_center_y = (bottom - top) / 2
            
            offset_y = visual_center_y - slot_center_y
            
            # Horizontal centering
            visual_center_x = (x_min + x_max) / 2
            width_center = arr.shape[1] / 2
            offset_x = visual_center_x - width_center
            
            print(f"DEBUG: {name} visual_h={visual_h}, visual_center_y={visual_center_y:.2f}, slot_center_y={slot_center_y:.2f}")
            print(f"DEBUG: {name} visual_w={x_max - x_min}, visual_center_x={visual_center_x:.2f}, width_center={width_center:.2f}")
            print(f"{name}: Y Offset={offset_y:.2f}, X Offset={offset_x:.2f}")
            
            if abs(offset_y) < 1.0:
                 print("  Result Y: Perfectly centered")
            else:
                 print(f"  Result Y: Offset by {offset_y:.2f}")
                 
            if abs(offset_x) < 2.0: # Allow slightly more for odd widths
                 print("  Result X: Perfectly centered")
            else:
                 print(f"  Result X: Offset by {offset_x:.2f}")
        else:
            print(f"{name}: No content found in slot {top}-{bottom}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            analyze_image(arg)
    else:
        for f in ["repro_final_surah_1.png", "repro_final_surah_2.png"]:
             if os.path.exists(f):
                 analyze_image(f)