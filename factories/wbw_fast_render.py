import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from factories.video import get_resolution
from factories.font_utils import resolve_font_path
from processes.video_configs import (
    BACKGROUND_OPACITY, BACKGROUND_RGB, FONT_COLOR, COMMON, FOOTER_CONFIG,
    get_arabic_text_position, get_translation_text_position,
    get_arabic_textbox_size, get_translation_textbox_size,
    get_reciter_info_position, get_surah_info_position, get_channel_info_position
)
from config_manager import config_manager

FONT_CACHE = {}

def hex_to_rgb(hex_color: str):
    if not hex_color:
        return (0, 0, 0)
    if isinstance(hex_color, tuple):
        return hex_color
    hex_color = hex_color.lstrip('#')
    if hex_color.startswith('rgb('):
        try:
             return tuple(map(int, hex_color.replace("rgb(", "").replace(")", "").split(",")))
        except:
             return (255, 255, 255)
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
        
        # Load fonts from config
        self.arabic_font_name = COMMON["arabic_textbox_config"].get("font", "me_quran.ttf")
        self.translation_font_name = COMMON["translation_textbox_config"].get("font", "kalpurush.ttf")
        
        self.arabic_font_path = resolve_font_path(self.arabic_font_name)
        self.translation_font_path = resolve_font_path(self.translation_font_name)
        
        self.font_color = hex_to_rgb(FONT_COLOR)
        
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

    def _draw_text_with_shadow(self, draw, text, position, font, fill="white", shadow_color=(0,0,0,128), shadow_offset=(2, 2)):
        # Draw shadow
        draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]), text, font=font, fill=shadow_color)
        # Draw main text
        draw.text(position, text, font=font, fill=fill)

    def _draw_footer(self, draw):
        """Renders the footer (Reciter, Surah, Brand)."""
        if not COMMON.get("enable_footer", True):
            return
            
        footer_font = self._get_font(self.translation_font_path, FOOTER_CONFIG["fontsize"])
        
        # 1. Reciter
        if COMMON.get("enable_reciter_info", True):
            reciter_name = self.scene_data.get("reciter_name", "")
            if reciter_name:
                # get_reciter_info_position returns (x_ratio, y_ratio)
                pos_r = get_reciter_info_position(self.is_short, 0)
                px = int(self.width * pos_r[0])
                py = int(self.height * pos_r[1])
                self._draw_text_with_shadow(draw, reciter_name, (px, py), footer_font, fill=self.font_color)
                
        # 2. Surah Info
        if COMMON.get("enable_surah_info", True):
            surah_name = self.scene_data.get("surah_name", "")
            verse_num = self.scene_data.get("verse_number", 0)
            surah_text = f"{surah_name} : {verse_num}" if verse_num > 0 else surah_name
            if surah_text:
                bbox = draw.textbbox((0, 0), surah_text, font=footer_font)
                sw = bbox[2] - bbox[0]
                pos_s = get_surah_info_position(self.is_short, sw)
                px = int(self.width * pos_s[0]) - (sw // 2)
                py = int(self.height * pos_s[1])
                self._draw_text_with_shadow(draw, surah_text, (px, py), footer_font, fill=self.font_color)
                
        # 3. Brand Info
        if COMMON.get("enable_channel_info", True):
            brand_name = self.scene_data.get("brand_name", "Taqwa")
            if brand_name:
                bbox = draw.textbbox((0, 0), brand_name, font=footer_font)
                bw = bbox[2] - bbox[0]
                pos_b = get_channel_info_position(self.is_short, bw)
                px = int(self.width * pos_b[0]) - bw
                py = int(self.height * pos_b[1])
                self._draw_text_with_shadow(draw, brand_name, (px, py), footer_font, fill=self.font_color)

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
        
        words = self.scene_data.get("words", [])
        translations = self.scene_data.get("translations", [])
        arabic_text = " ".join(words)
        trans_text = " ".join(translations)

        if self.layout == "standard":
            # --- Standard Layout Logic ---
            arabic_config = get_arabic_textbox_size(self.is_short, arabic_text)
            trans_config = get_translation_textbox_size(self.is_short, trans_text)
            
            arabic_font = self._get_font(self.arabic_font_path, arabic_config["fontsize"])
            trans_font = self._get_font(self.translation_font_path, trans_config["fontsize"])
            
            # Position calculation (Match MoviePy logic)
            # MoviePy Arabic position: get_arabic_text_position(is_short, arabic_clip.h)
            # We need to estimate text height first
            bbox_a = draw.textbbox((0, 0), arabic_text, font=arabic_font)
            wa = bbox_a[2] - bbox_a[0]
            ha = bbox_a[3] - bbox_a[1]
            
            arabic_y = get_arabic_text_position(self.is_short, ha)
            arabic_pos = ((self.width - wa) // 2, arabic_y)
            
            self._draw_text_with_shadow(draw, arabic_text, arabic_pos, arabic_font, fill=self.font_color)
            
            # MoviePy Translation position: get_translation_text_position(is_short)
            bbox_t = draw.textbbox((0, 0), trans_text, font=trans_font)
            wt = bbox_t[2] - bbox_t[0]
            
            trans_y = get_translation_text_position(self.is_short)
            trans_pos = ((self.width - wt) // 2, trans_y)
            
            self._draw_text_with_shadow(draw, trans_text, trans_pos, trans_font, fill=self.font_color)
            
            # Dummy rects for highlights (Phase 2 Task 2)
            # We'll refine this in Task 5 (parity)
            self.word_rects = []
            current_x = arabic_pos[0]
            for _ in words:
                 self.word_rects.append([current_x, arabic_pos[1], current_x + 80, arabic_pos[1] + ha])
                 current_x += 100
        elif self.layout == "interlinear":
            # --- Interlinear Layout Logic (Match factories/single_clip.py) ---
            space_width = 15
            arabic_font_size = int(config_manager.get("WBW_FONT_SIZE_REGULAR", 60))
            if self.is_short:
                 arabic_font_size = int(config_manager.get("WBW_FONT_SIZE_SHORT", 40))
            
            trans_font_size = int(config_manager.get("WBW_TRANSLATION_FONT_SIZE", 20))
            
            arabic_font = self._get_font(self.arabic_font_path, arabic_font_size)
            trans_font = self._get_font(self.translation_font_path, trans_font_size)
            
            processed_blocks = []
            total_width = 0
            
            for i in range(len(words)):
                word = words[i]
                trans = translations[i] if i < len(translations) else ""
                
                # Arabic bbox
                bbox_a = draw.textbbox((0, 0), word, font=arabic_font)
                aw = bbox_a[2] - bbox_a[0]
                ah = bbox_a[3] - bbox_a[1]
                
                # Translation bbox
                bbox_t = draw.textbbox((0, 0), trans, font=trans_font)
                tw = bbox_t[2] - bbox_t[0]
                th = bbox_t[3] - bbox_t[1]
                
                block_w = max(aw, tw)
                processed_blocks.append({
                    "word": word,
                    "trans": trans,
                    "aw": aw, "ah": ah,
                    "tw": tw, "th": th,
                    "block_w": block_w
                })
                total_width += block_w
                if i < len(words) - 1:
                    total_width += space_width
            
            max_ah = max((b["ah"] for b in processed_blocks), default=0)
            max_th = max((b["th"] for b in processed_blocks), default=0)
            line_height = max_ah + 5 + 3 + 5 + max_th
            
            arabic_y_base = get_arabic_text_position(self.is_short, line_height)
            
            curr_x = (self.width + total_width) // 2 # Center the whole line
            
            self.word_rects = []
            # RTL loop
            for block in processed_blocks:
                curr_x -= block["block_w"]
                
                # Arabic position
                ax = curr_x + (block["block_w"] - block["aw"]) // 2
                ay = arabic_y_base
                self._draw_text_with_shadow(draw, block["word"], (ax, ay), arabic_font, fill=self.font_color)
                
                # Underline
                ux = ax
                uy = ay + block["ah"] + 2
                draw.rectangle([ux, uy, ux + block["aw"], uy + 3], fill=self.font_color)
                
                # Translation position
                tx = curr_x + (block["block_w"] - block["tw"]) // 2
                ty = uy + 3 + 5
                self._draw_text_with_shadow(draw, block["trans"], (tx, ty), trans_font, fill=self.font_color)
                
                # Highlight rect (around Arabic word)
                self.word_rects.append([ax - 5, ay - 5, ax + block["aw"] + 5, ay + block["ah"] + 5])
                
                curr_x -= space_width
        else:
            self.word_rects = []
            
        # 3. Draw Footer
        self._draw_footer(draw)

        # 4. Cache the base frame
        self._pre_rendered_frames[-1] = np.array(self.static_base.convert('RGB'))
        
        # 5. Pre-render highlight frames
        highlight_color = (255, 255, 0, 60) # Yellow with 23% alpha
        for i, rect in enumerate(self.word_rects):
            overlay = Image.new('RGBA', self.resolution, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            draw_overlay.rectangle(rect, fill=highlight_color)
            combined = Image.alpha_composite(self.static_base, overlay)
            self._pre_rendered_frames[i] = np.array(combined.convert('RGB'))

    def get_frame_at(self, timestamp_sec: float) -> np.ndarray:
        """Returns a numpy array (RGB) representing the frame at the given timestamp."""
        if not self._pre_rendered_frames:
            self.prepare_static_base()
            
        timestamp_ms = int(timestamp_sec * 1000)
        
        active_idx = -1
        word_segments = self.scene_data.get("word_segments", [])
        
        if word_segments:
            for i, segment in enumerate(word_segments):
                if segment["start_ms"] <= timestamp_ms < segment["end_ms"]:
                    active_idx = i
                    break
        else:
            # Fallback if no word_segments provided (basic scene highlight)
            start_ms = self.scene_data.get("start_ms", 0)
            end_ms = self.scene_data.get("end_ms", 0)
            if start_ms <= timestamp_ms <= end_ms:
                active_idx = 0
        
        # We use active_idx to pick the right pre-rendered frame
        # If active_idx is not in _pre_rendered_frames, use the base frame (-1)
        frame = self._pre_rendered_frames.get(active_idx, self._pre_rendered_frames.get(-1))
        
        # If we still don't have a frame, return a black image
        if frame is None:
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
        return frame.copy()
