import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from factories.video import get_resolution
from factories.font_utils import resolve_font_path
from factories.complex_text import render_complex_text_to_pil
from processes.video_configs import (
    BACKGROUND_OPACITY, BACKGROUND_RGB, FONT_COLOR, COMMON, FOOTER_CONFIG,
    get_arabic_text_position, get_translation_text_position,
    get_arabic_textbox_size, get_translation_textbox_size,
    get_reciter_info_position, get_surah_info_position, get_channel_info_position,
    get_full_ayah_translation_position
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
        Initializes the high-speed WBW renderer for a single scene (ayah/line).
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

    def _draw_complex_text_with_shadow(self, text, position, font_path, font_size, fill="white", shadow_color=(0,0,0,128), shadow_offset=(2, 2)):
        """Renders complex text (shaped) with a shadow by pasting onto static_base."""
        font_color_str = fill
        if not isinstance(font_color_str, str):
            font_color_str = f"rgb({font_color_str[0]},{font_color_str[1]},{font_color_str[2]})"
            
        shadow_color_str = shadow_color
        if not isinstance(shadow_color_str, str) and len(shadow_color_str) >= 3:
            shadow_color_str = f"rgb({shadow_color_str[0]},{shadow_color_str[1]},{shadow_color_str[2]})"

        # 1. Draw shadow
        shadow_img = render_complex_text_to_pil(text, font_path, font_size, shadow_color_str)
        if shadow_img:
            sx, sy = position[0] + shadow_offset[0], position[1] + shadow_offset[1]
            self.static_base.paste(shadow_img, (sx, sy), shadow_img)
            
        # 2. Draw main text
        main_img = render_complex_text_to_pil(text, font_path, font_size, font_color_str)
        if main_img:
            self.static_base.paste(main_img, position, main_img)
        
        return main_img.size if main_img else (0, 0)

    def _draw_footer(self, draw):
        """Renders the footer (Reciter, Surah, Brand)."""
        if not COMMON.get("enable_footer", True):
            return
            
        footer_font_size = FOOTER_CONFIG["fontsize"]
        
        # 1. Reciter
        if COMMON.get("enable_reciter_info", True):
            reciter_name = self.scene_data.get("reciter_name", "")
            if reciter_name:
                pos_r = get_reciter_info_position(self.is_short, 0)
                px = int(self.width * pos_r[0])
                py = int(self.height * pos_r[1])
                # Footers might be complex (Bengali reciter names?)
                self._draw_complex_text_with_shadow(reciter_name, (px, py), self.translation_font_path, footer_font_size, fill=self.font_color)
                
        # 2. Surah Info
        if COMMON.get("enable_surah_info", True):
            surah_name = self.scene_data.get("surah_name", "")
            verse_num = self.scene_data.get("verse_number", 0)
            surah_text = f"{surah_name} : {verse_num}" if verse_num > 0 else surah_name
            if surah_text:
                # Get size via complex renderer to be safe
                temp_img = render_complex_text_to_pil(surah_text, self.translation_font_path, footer_font_size, "white")
                sw = temp_img.width if temp_img else 0
                pos_s = get_surah_info_position(self.is_short, sw)
                px = int(self.width * pos_s[0]) - (sw // 2)
                py = int(self.height * pos_s[1])
                self._draw_complex_text_with_shadow(surah_text, (px, py), self.translation_font_path, footer_font_size, fill=self.font_color)
                
        # 3. Brand Info
        if COMMON.get("enable_channel_info", True):
            brand_name = self.scene_data.get("brand_name", "Taqwa")
            if brand_name:
                temp_img = render_complex_text_to_pil(brand_name, self.translation_font_path, footer_font_size, "white")
                bw = temp_img.width if temp_img else 0
                pos_b = get_channel_info_position(self.is_short, bw)
                px = int(self.width * pos_b[0]) - bw
                py = int(self.height * pos_b[1])
                self._draw_complex_text_with_shadow(brand_name, (px, py), self.translation_font_path, footer_font_size, fill=self.font_color)

    def _draw_full_translation(self, draw):
        """Renders the full ayah translation overlay at the bottom."""
        full_text = self.scene_data.get("full_ayah_translation", "")
        if not full_text:
            return
            
        font_size = int(config_manager.get("WBW_FULL_TRANSLATION_FONT_SIZE", 30))
        font = self._get_font(self.translation_font_path, font_size)
        
        max_width = int(self.width * 0.9)
        lines = []
        words = full_text.split()
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 10
        total_h = len(lines) * line_height
        
        y_base = get_full_ayah_translation_position(self.is_short)
        
        # Draw background box
        bg_padding = 20
        box_y0 = y_base - bg_padding
        box_y1 = y_base + total_h + bg_padding
        box_x0 = (self.width - max_width) // 2 - bg_padding
        box_x1 = (self.width + max_width) // 2 + bg_padding
        from factories.complex_text import render_complex_text_to_pil

        font_color_str = FONT_COLOR
        if not isinstance(font_color_str, str):
            font_color_str = f"rgb({font_color_str[0]},{font_color_str[1]},{font_color_str[2]})"

        # Use alpha composite for background box
        overlay = Image.new('RGBA', self.resolution, (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)
        d_overlay.rectangle([box_x0, box_y0, box_x1, box_y1], fill=(0, 0, 0, 153))
        self.static_base.alpha_composite(overlay)

        curr_y = y_base
        for line in lines:
            # Use complex text factory for proper shaping
            line_img = render_complex_text_to_pil(line, self.translation_font_path, font_size, font_color_str)

            # Center the rendered line on our base
            lw, lh = line_img.size
            lx = (self.width - lw) // 2

            # Paste with alpha
            self.static_base.paste(line_img, (lx, curr_y), line_img)
            curr_y += line_height

    def prepare_static_base(self):
        """Renders the background and all static text (Arabic + Translation)."""
        is_video_bg = self.background_path and (self.background_path.endswith('.mp4') or self.background_path.endswith('.mov'))
        
        if is_video_bg:
            self.static_base = Image.new('RGBA', self.resolution, (0, 0, 0, 0))
        elif self.background_path and os.path.exists(self.background_path):
            self.static_base = Image.open(self.background_path).convert('RGBA')
            self.static_base = self.static_base.resize(self.resolution, Image.Resampling.LANCZOS)
        else:
            bg_color = hex_to_rgb(config_manager.get("BACKGROUND_RGB", "#000000"))
            rgba_color = bg_color + (255,)
            self.static_base = Image.new('RGBA', self.resolution, rgba_color)
            
        if not is_video_bg:
            dimming = float(config_manager.get("MUSHAF_BACKGROUND_DIMMING", "0.3"))
            if dimming > 0:
                overlay = Image.new('RGBA', self.resolution, (0, 0, 0, int(dimming * 255)))
                self.static_base.alpha_composite(overlay)

        draw = ImageDraw.Draw(self.static_base)
        
        words = self.scene_data.get("words", [])
        translations = self.scene_data.get("translations", [])
        arabic_text = " ".join(words)
        trans_text = " ".join(translations)

        if self.layout == "standard":
            arabic_config = get_arabic_textbox_size(self.is_short, arabic_text)
            trans_config = get_translation_textbox_size(self.is_short, trans_text)
            arabic_font = self._get_font(self.arabic_font_path, arabic_config["fontsize"])
            
            # 1. Arabic Text (Direct draw is usually OK for Mushaf fonts or use complex if needed)
            bbox_a = draw.textbbox((0, 0), arabic_text, font=arabic_font)
            wa = bbox_a[2] - bbox_a[0]
            ha = bbox_a[3] - bbox_a[1]
            arabic_y = get_arabic_text_position(self.is_short, ha)
            arabic_pos = ((self.width - wa) // 2, arabic_y)
            self._draw_text_with_shadow(draw, arabic_text, arabic_pos, arabic_font, fill=self.font_color)
            
            # 2. Translation Text (Complex Shaping)
            trans_font_size = trans_config["fontsize"]
            # Get width via complex renderer
            temp_img = render_complex_text_to_pil(trans_text, self.translation_font_path, trans_font_size, "white")
            wt = temp_img.width if temp_img else 0
            trans_y = get_translation_text_position(self.is_short)
            trans_pos = ((self.width - wt) // 2, trans_y)
            self._draw_complex_text_with_shadow(trans_text, trans_pos, self.translation_font_path, trans_font_size, fill=self.font_color)

            self.word_rects = []
            space_w = draw.textbbox((0, 0), " ", font=arabic_font)[2] - draw.textbbox((0, 0), " ", font=arabic_font)[0]
            current_x = arabic_pos[0] + wa
            for word in words:
                 bbox_w = draw.textbbox((0, 0), word, font=arabic_font)
                 word_w = bbox_w[2] - bbox_w[0]
                 wx = current_x - word_w
                 self.word_rects.append([wx - 5, arabic_pos[1] - 5, current_x + 5, arabic_pos[1] + ha + 5])
                 current_x -= (word_w + space_w)
        elif self.layout == "interlinear":
            space_width = 15
            arabic_font_size = int(config_manager.get("WBW_FONT_SIZE_REGULAR", 60))
            if self.is_short: arabic_font_size = int(config_manager.get("WBW_FONT_SIZE_SHORT", 40))
            trans_font_size = int(config_manager.get("WBW_TRANSLATION_FONT_SIZE", 20))
            arabic_font = self._get_font(self.arabic_font_path, arabic_font_size)
            
            processed_blocks = []
            total_width = 0
            for i in range(len(words)):
                word = words[i]
                trans = translations[i] if i < len(translations) else ""
                
                # Arabic size
                bbox_a = draw.textbbox((0, 0), word, font=arabic_font)
                aw = bbox_a[2] - bbox_a[0]
                ah = bbox_a[3] - bbox_a[1]
                
                # Translation size (Complex)
                t_img = render_complex_text_to_pil(trans, self.translation_font_path, trans_font_size, "white")
                tw = t_img.width if t_img else 0
                th = t_img.height if t_img else 0
                
                block_w = max(aw, tw)
                processed_blocks.append({"word": word, "trans": trans, "aw": aw, "ah": ah, "tw": tw, "th": th, "block_w": block_w})
                total_width += block_w
                if i < len(words) - 1: total_width += space_width
                
            max_ah = max((b["ah"] for b in processed_blocks), default=0)
            max_th = max((b["th"] for b in processed_blocks), default=0)
            line_height = max_ah + 5 + 3 + 5 + max_th
            arabic_y_base = get_arabic_text_position(self.is_short, line_height)
            curr_x = (self.width + total_width) // 2 
            self.word_rects = []
            for block in processed_blocks:
                curr_x -= block["block_w"]
                ax = curr_x + (block["block_w"] - block["aw"]) // 2
                ay = arabic_y_base
                # Arabic word
                self._draw_text_with_shadow(draw, block["word"], (ax, ay), arabic_font, fill=self.font_color)
                ux = ax
                uy = ay + block["ah"] + 2
                draw.rectangle([ux, uy, ux + block["aw"], uy + 3], fill=self.font_color)
                
                # Complex translation word
                tx = curr_x + (block["block_w"] - block["tw"]) // 2
                ty = uy + 3 + 5
                self._draw_complex_text_with_shadow(block["trans"], (tx, ty), self.translation_font_path, trans_font_size, fill=self.font_color)
                
                self.word_rects.append([ax - 5, ay - 5, ax + block["aw"] + 5, ay + block["ah"] + 5])
                curr_x -= space_width
        else:
            self.word_rects = []
            
        self._draw_footer(draw)
        self._draw_full_translation(draw)

        mode = 'RGBA' if is_video_bg else 'RGB'
        self._pre_rendered_frames[-1] = np.array(self.static_base.convert(mode))
        
        highlight_color = (255, 255, 0, 60)
        for i, rect in enumerate(self.word_rects):
            overlay = Image.new('RGBA', self.resolution, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            draw_overlay.rectangle(rect, fill=highlight_color)
            combined = Image.alpha_composite(self.static_base, overlay)
            self._pre_rendered_frames[i] = np.array(combined.convert(mode))

    def get_frame_at(self, timestamp_sec: float) -> np.ndarray:
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
            start_ms = self.scene_data.get("start_ms", 0)
            end_ms = self.scene_data.get("end_ms", 0)
            if start_ms <= timestamp_ms <= end_ms:
                active_idx = 0
        frame = self._pre_rendered_frames.get(active_idx, self._pre_rendered_frames.get(-1))
        if frame is None:
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
        return frame.copy()

class FastWBWVideoRenderer:
    def __init__(self, scenes: list, is_short: bool = False):
        self.scenes = scenes
        self.is_short = is_short
        self.resolution = get_resolution(is_short)
        self.width, self.height = self.resolution
        self._last_scene_idx = 0
        
    def get_frame_at(self, timestamp_sec: float) -> np.ndarray:
        for i in range(self._last_scene_idx, len(self.scenes)):
            scene = self.scenes[i]
            if scene["start_sec"] <= timestamp_sec < scene["end_sec"]:
                self._last_scene_idx = i
                return scene["renderer"].get_frame_at(timestamp_sec - scene["start_sec"])
        for i in range(len(self.scenes)):
            scene = self.scenes[i]
            if scene["start_sec"] <= timestamp_sec < scene["end_sec"]:
                self._last_scene_idx = i
                return scene["renderer"].get_frame_at(timestamp_sec - scene["start_sec"])
        if self.scenes and timestamp_sec >= self.scenes[-1]["end_sec"]:
             return self.scenes[-1]["renderer"].get_frame_at(self.scenes[-1]["end_sec"] - self.scenes[-1]["start_sec"] - 0.01)
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)
