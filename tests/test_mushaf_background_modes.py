import numpy as np
from factories.single_clip import generate_mushaf_border_clip

def test_border_clip_transparency():
    size = (100, 100)
    # Transparent Mode: Alpha should be 0 in the middle
    clip = generate_mushaf_border_clip(size, 2, 5, (255, 255, 255), 0, 1.0, bg_mode="Transparent")
    # Mask is a separate clip, values are 0.0 to 1.0
    mask_frame = clip.mask.get_frame(0)
    # Center pixel alpha
    assert mask_frame[50, 50] == 0.0

def test_border_clip_solid():
    size = (100, 100)
    # Solid Mode: Alpha should be 1.0 in the middle
    clip = generate_mushaf_border_clip(size, 2, 5, (212, 197, 161), 0, 1.0, bg_mode="Solid", bg_color="#FFFDF5")       
    mask_frame = clip.mask.get_frame(0)
    assert mask_frame[50, 50] == 1.0
    # Check color
    frame = clip.get_frame(0)
    assert 250 <= frame[50, 50, 0] <= 255
    assert 248 <= frame[50, 50, 1] <= 255
    assert 240 <= frame[50, 50, 2] <= 250

def test_border_clip_semi():
    size = (100, 100)
    # Semi-Transparent: Alpha should be approx 0.5 (128/255)
    clip = generate_mushaf_border_clip(size, 2, 5, (212, 197, 161), 0, 1.0, bg_mode="Semi-Transparent", bg_color="#000000")
    mask_frame = clip.mask.get_frame(0)
    assert 0.49 <= mask_frame[50, 50] <= 0.51
