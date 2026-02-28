import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from factories.video import get_resolution
from factories.font_utils import resolve_font_path
from processes.video_configs import BACKGROUND_OPACITY, BACKGROUND_RGB, FONT_COLOR, COMMON
from config_manager import config_manager

FONT_CACHE = {}

def hex_to_rgb(hex_color: str):
    if not hex_color:
        return (0, 0, 0)
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class WBWFastRenderer:
    def __init__(self, scene_data: dict, background_path: str = None, resolution: tuple = None):
        """
        Initializes the high-speed WBW renderer.
        """
        self.scene_data = scene_data
        self.is_short = scene_data.get("is_short", False)
        self.layout = scene_data.get("layout", "standard")
        
        if resolution:
            self.resolution = resolution
        else:
            self.resolution = get_resolution(self.is_short)
            
        self.width, self.height = self.resolution
        self.background_path = background_path
        
        # Load fonts
        self.arabic_font_path = resolve_font_path("me_quran.ttf")
        self.translation_font_path = resolve_font_path("kalpurush.ttf")
        
        self.static_base = None # Cached PIL Image (RGBA)
        self._pre_rendered_frames = {} # Cache for highlight frames
        self.word_rects = [] # Bounding boxes for each word [x0, y0, x1, y1]
        
    def _get_font(self, path, size):
        key = f"{path}_{size}"
        if key not in FONT_CACHE:
            try:
                FONT_CACHE[key] = ImageFont.truetype(path, size)
            except:
                FONT_CACHE[key] = ImageFont.load_default()
        return FONT_CACHE[key]

    def prepare_static_base(self):
        """Renders the background and all static text (Arabic + Translation)."""
        # 1. Initialize background
        if self.background_path and os.path.exists(self.background_path):
            self.static_base = Image.open(self.background_path).convert('RGBA')
            self.static_base = self.static_base.resize(self.resolution, Image.Resampling.LANCZOS)
        else:
            # Fallback to standard background color logic
            bg_color = hex_to_rgb(config_manager.get("BACKGROUND_RGB", "#000000"))
            rgba_color = bg_color + (255,)
            self.static_base = Image.new('RGBA', self.resolution, rgba_color)
            
        # Apply global dimming if configured
        dimming = float(config_manager.get("MUSHAF_BACKGROUND_DIMMING", "0.3"))
        if dimming > 0:
            overlay = Image.new('RGBA', self.resolution, (0, 0, 0, int(dimming * 255)))
            self.static_base.alpha_composite(overlay)

        # 2. Draw static text
        draw = ImageDraw.Draw(self.static_base)
        
        # Simplified drawing for skeleton:
        # We need to calculate positions based on layout
        words = self.scene_data.get("words", [])
        translations = self.scene_data.get("translations", [])
        
        # Placeholder for standard layout (stacked)
        # In a real implementation, we'd render word-by-word to get rects
        arabic_size = 80
        trans_size = 40
        arabic_font = self._get_font(self.arabic_font_path, arabic_size)
        trans_font = self._get_font(self.translation_font_path, trans_size)
        
        # For the skeleton, just render the whole lines centered
        arabic_text = " ".join(words)
        trans_text = " ".join(translations)
        
        # Arabic line (RTL handled by reversing if needed, but Pillow handles some RTL)
        # Actually for QPC v2 we might need reversal.
        # me_quran.ttf usually needs proper shaping.
        
        # Position calculation
        y_center = self.height // 2
        
        # Draw Arabic
        bbox_a = draw.textbbox((0, 0), arabic_text, font=arabic_font)
        wa = bbox_a[2] - bbox_a[0]
        draw.text(((self.width - wa) // 2, y_center - 100), arabic_text, font=arabic_font, fill="white")
        
        # Draw Translation
        bbox_t = draw.textbbox((0, 0), trans_text, font=trans_font)
        wt = bbox_t[2] - bbox_t[0]
        draw.text(((self.width - wt) // 2, y_center + 50), trans_text, font=trans_font, fill="white")
        
        # Pre-calculate a dummy highlight for the first word for testing
        # In Phase 2, this will be precise.
        self.word_rects = [[(self.width - wa) // 2, y_center - 120, (self.width - wa) // 2 + 100, y_center - 20]]

        # 3. Cache the base frame
        self._pre_rendered_frames[-1] = np.array(self.static_base.convert('RGB'))
        
        # 4. Pre-render highlight frames
        highlight_color = (255, 255, 0, 60) # Yellow with 23% alpha
        for i, rect in enumerate(self.word_rects):
            overlay = Image.new('RGBA', self.resolution, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            draw_overlay.rectangle(rect, fill=highlight_color)
            combined = Image.alpha_composite(self.static_base, overlay)
            self._pre_rendered_frames[i] = np.array(combined.convert('RGB'))

    def get_frame_at(self, timestamp_sec: float) -> np.ndarray:
        """Returns a numpy array (RGB) representing the frame at the given timestamp."""
        if self.static_base is None:
            self.prepare_static_base()
            
        timestamp_ms = timestamp_sec * 1000
        start_ms = self.scene_data.get("start_ms", 0)
        end_ms = self.scene_data.get("end_ms", 0)
        
        active_idx = -1
        # In a real implementation, we'd loop through word segments
        # For now, just a dummy check for the first word
        if start_ms <= timestamp_ms <= end_ms:
            active_idx = 0
        
        frame = self._pre_rendered_frames.get(active_idx, self._pre_rendered_frames[-1]).copy()
        return frame
