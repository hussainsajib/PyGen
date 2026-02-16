import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from factories.video import get_resolution
from factories.font_utils import resolve_font_path
from processes.video_configs import BACKGROUND_OPACITY, BACKGROUND_RGB, FONT_COLOR
from config_manager import config_manager

# Load ligature data for Mushaf headers
LIGATURE_DATA = {}
try:
    ligature_path = os.path.abspath(os.path.join("databases", "text", "ligatures.json"))
    if os.path.exists(ligature_path):
        with open(ligature_path, "r", encoding="utf-8") as f:
            LIGATURE_DATA = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load ligatures.json: {e}")

FONT_CACHE = {}

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class MushafRenderer:
    def __init__(self, page_number: int, is_short: bool, lines: list, font_scale: float = 0.8, background_input: str = None, 
                 reciter_name: str = None, surah_name: str = None, brand_name: str = None, total_duration_ms: float = 0,
                 surah_number: int = None, render_mode: str = "main"):
        self.page_number = page_number
        self.is_short = is_short
        self.lines = lines
        self.font_scale = font_scale
        self.background_input = background_input
        self.resolution = get_resolution(is_short)
        self.width, self.height = self.resolution
        
        self.reciter_name = reciter_name
        self.surah_name = surah_name
        self.brand_name = brand_name
        self.total_duration_ms = total_duration_ms
        self.surah_number = surah_number
        self.render_mode = render_mode # "main", "intro", "ending"
        
        self.font_paths = {
            "page": os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page_number}.ttf")),
            "bsml": os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF")),
            "sura": os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf")),
            "footer": resolve_font_path("kalpurush.ttf")
        }
        if not os.path.exists(self.font_paths["page"]):
            self.font_paths["page"] = "Arial"

        self.line_height = (self.height * 0.8) / 15
        self.static_base = None
        self.renderable_lines = []
        self.line_positions = []
        self.highlight_rects = {} 
        self._footer_font = None 
        self._pre_rendered_frames = {} 
        
        if self.render_mode == "main":
            self._prepare_renderable_lines()

    def _prepare_renderable_lines(self):
        from factories.single_clip import calculate_mushaf_font_size
        
        for line in self.lines:
            l_type = line.get("line_type", "ayah")
            words = line.get("words", [])
            text = "".join([w["text"] for w in reversed(words)])
            if l_type == "basmallah" and not text:
                text = "\u00F3"
            if not text and l_type != "surah_name":
                continue
            self.renderable_lines.append(line)
            
        has_header = any(l.get("line_type") == "surah_name" for l in self.renderable_lines)
        has_bsml = any(l.get("line_type") == "basmallah" for l in self.renderable_lines)
        has_header_gap = has_header and has_bsml
        
        from factories.single_clip import calculate_mushaf_content_y_positions
        self.line_positions = calculate_mushaf_content_y_positions(self.height, len(self.renderable_lines), has_header_gap)
        
        # Pre-calculate highlight rectangles
        for i, line in enumerate(self.renderable_lines):
            l_type = line.get("line_type", "ayah")
            if l_type in ["basmallah", "surah_name"]:
                continue
            
            words = line.get("words", [])
            text = "".join([w["text"] for w in reversed(words)])
            font_size = calculate_mushaf_font_size(self.width, self.line_height, l_type, self.font_scale)
            
            cache_key = f"{self.font_paths['page']}_{font_size}"
            if cache_key not in FONT_CACHE:
                FONT_CACHE[cache_key] = ImageFont.truetype(self.font_paths['page'], font_size)
            font = FONT_CACHE[cache_key]
            
            dummy_img = Image.new('RGBA', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            h_width = text_w + 20
            
            y_pos = self.line_positions[i]
            x0 = (self.width - h_width) // 2
            y0 = y_pos
            x1 = x0 + h_width
            y1 = y0 + int(self.line_height)
            self.highlight_rects[i] = [int(x0), int(y0), int(x1), int(y1)]

    def prepare_static_base(self):
        """Renders the background, border, and static text once."""
        if self.render_mode == "main":
            from factories.single_clip import pre_render_static_page
            self.static_base = pre_render_static_page(
                resolution=self.resolution,
                background_input=self.background_input,
                renderable_lines=self.renderable_lines,
                line_positions=self.line_positions,
                line_height=self.line_height,
                font_paths=self.font_paths,
                font_scale=self.font_scale
            )
            
            # Pre-render overlays onto static_base (RGBA)
            draw = ImageDraw.Draw(self.static_base, 'RGBA')
            self._draw_overlays(draw)
        else:
            # Intro or Ending mode
            from factories.single_clip import get_pil_background, draw_mushaf_border_onto
            self.static_base = get_pil_background(self.background_input, self.resolution)
            
            # Apply Dimming
            try:
                dimming_opacity = float(config_manager.get("MUSHAF_BACKGROUND_DIMMING", "0.0"))
            except (ValueError, TypeError):
                dimming_opacity = 0.0
                
            if dimming_opacity > 0:
                overlay = Image.new('RGBA', self.resolution, (0, 0, 0, int(dimming_opacity * 255)))
                self.static_base.alpha_composite(overlay)
                
            # Draw Border
            top_margin = self.height * 0.1
            bottom_margin = self.height * 0.1
            usable_height = self.height - top_margin - bottom_margin
            bg_mode = config_manager.get("MUSHAF_PAGE_BACKGROUND_MODE", "Solid")
            bg_color = config_manager.get("MUSHAF_PAGE_COLOR", "#FFFDF5")
            try:
                opacity_percent = int(config_manager.get("MUSHAF_PAGE_OPACITY", "90"))
            except (ValueError, TypeError):
                opacity_percent = 90
            bg_opacity = int((opacity_percent / 100) * 255)
            
            self.static_base = draw_mushaf_border_onto(self.static_base, usable_height, bg_mode, bg_color, bg_opacity)
            
            draw = ImageDraw.Draw(self.static_base, 'RGBA')
            if self.render_mode == "intro":
                self._draw_intro_screen(draw)
            elif self.render_mode == "ending":
                self._draw_ending_screen(draw)
        
        # Base frame (no highlights) - convert to RGB numpy
        self._pre_rendered_frames[-1] = np.array(self.static_base.convert('RGB'))
        
        # Highlighted frames (only relevant for main mode)
        if self.render_mode == "main":
            highlight_color = (255, 255, 0, 25) # Yellow with 10% alpha
            for i in self.highlight_rects:
                # Create a transparent layer for the highlight
                overlay = Image.new('RGBA', self.static_base.size, (0, 0, 0, 0))
                draw_overlay = ImageDraw.Draw(overlay)
                draw_overlay.rectangle(self.highlight_rects[i], fill=highlight_color)
                
                # Composite the highlight overlay onto the static base
                combined = Image.alpha_composite(self.static_base, overlay)
                self._pre_rendered_frames[i] = np.array(combined.convert('RGB'))

    def _get_footer_font(self):
        if self._footer_font:
            return self._footer_font
            
        from processes.video_configs import FOOTER_CONFIG
        font_size = FOOTER_CONFIG.get("fontsize", 30)
        try:
            if os.path.exists(self.font_paths["footer"]):
                self._footer_font = ImageFont.truetype(self.font_paths["footer"], font_size)
            else:
                self._footer_font = ImageFont.load_default()
        except:
            self._footer_font = ImageFont.load_default()
        return self._footer_font

    def _draw_intro_screen(self, draw: ImageDraw.Draw):
        """Draws the intro screen with Surah/Para name and reciter."""
        from factories.complex_text import render_complex_text_to_pil
        
        font_path = self.font_paths["footer"]
        color = FONT_COLOR
        if isinstance(color, str) and color.startswith("rgb("):
            color = hex_to_rgb("#C9B59C")
            
        title_size = 80
        sub_size = 40
        
        # Title: Surah or Para Name
        title_text = self.surah_name or "Quran"
        title_img = render_complex_text_to_pil(title_text, font_path, title_size, color)
        
        # Sub-heading: Reciter Name
        sub_text = self.reciter_name or ""
        sub_img = render_complex_text_to_pil(sub_text, font_path, sub_size, color)
        
        # Position
        total_h = title_img.height + 20 + sub_img.height
        start_y = (self.height - total_h) // 2
        
        x_title = (self.width - title_img.width) // 2
        self.static_base.paste(title_img, (x_title, start_y), title_img)
        
        x_sub = (self.width - sub_img.width) // 2
        self.static_base.paste(sub_img, (x_sub, start_y + title_img.height + 20), sub_img)

    def _draw_ending_screen(self, draw: ImageDraw.Draw):
        """Draws the ending screen with branding and subscribe CTA."""
        from factories.complex_text import render_complex_text_to_pil
        
        font_path = self.font_paths["footer"]
        color = FONT_COLOR
        if isinstance(color, str) and color.startswith("rgb("):
            color = hex_to_rgb("#C9B59C")
            
        brand_size = 70
        cta_size = 35
        
        # Brand: Taqwa Bangla
        brand_text = "তাকওয়া বাংলা"
        brand_img = render_complex_text_to_pil(brand_text, font_path, brand_size, color)
        
        # CTA: Subscribe
        cta_text = "চ্যানেলটি সাবস্ক্রাইব করুন"
        cta_img = render_complex_text_to_pil(cta_text, font_path, cta_size, color)
        
        # Position
        total_h = brand_img.height + 25 + cta_img.height
        start_y = (self.height - total_h) // 2
        
        x_brand = (self.width - brand_img.width) // 2
        self.static_base.paste(brand_img, (x_brand, start_y), brand_img)
        
        x_cta = (self.width - cta_img.width) // 2
        self.static_base.paste(cta_img, (x_cta, start_y + brand_img.height + 25), cta_img)

    def _draw_overlays(self, draw: ImageDraw.Draw):
        """Draws horizontal footer with a semi-transparent background bar."""
        if config_manager.get("ENABLE_FOOTER", "True") != "True":
            return

        from factories.complex_text import render_complex_text_to_pil
        from processes.video_configs import FOOTER_CONFIG, get_reciter_info_position, get_surah_info_position, get_channel_info_position
        
        font_path = self.font_paths["footer"]
        font_size = FOOTER_CONFIG.get("fontsize", 30)
        
        color = FONT_COLOR
        if isinstance(color, str) and color.startswith("rgb("):
            color = hex_to_rgb("#C9B59C")
            
        # Footer Bar Dimensions
        bar_height = font_size + 30
        bottom_floating_margin = 20
        bar_y = self.height - bar_height - bottom_floating_margin - 10 # Slightly above progress bar
        
        # 2. Render and Position Items
        text_y = bar_y + (bar_height - font_size) // 2 - 2

        # Reciter Name (Left)
        if self.reciter_name and config_manager.get("ENABLE_RECITER_INFO", "True") == "True":
            img = render_complex_text_to_pil(self.reciter_name, font_path, font_size, color)
            pos_x_ratio = get_reciter_info_position(self.is_short, img.width)[0]
            x = int(self.width * pos_x_ratio)
            self.static_base.paste(img, (x, int(text_y)), img)

        # Surah Name (Center)
        if self.surah_name and config_manager.get("ENABLE_SURAH_INFO", "True") == "True":
            img = render_complex_text_to_pil(self.surah_name, font_path, font_size, color)
            x = (self.width - img.width) // 2
            self.static_base.paste(img, (int(x), int(text_y)), img)

        # Brand Name (Right)
        if self.brand_name and config_manager.get("ENABLE_CHANNEL_INFO", "True") == "True":
            img = render_complex_text_to_pil(self.brand_name, font_path, font_size, color)
            pos_x_ratio = get_channel_info_position(self.is_short, img.width)[0]
            x = int(self.width * pos_x_ratio) - img.width
            self.static_base.paste(img, (int(x), int(text_y)), img)

    def _draw_progress_bar_numpy(self, frame_np: np.ndarray, timestamp_ms: float):
        """Draws the progress bar directly onto the numpy array."""
        if self.total_duration_ms <= 0:
            return
            
        ratio = timestamp_ms / self.total_duration_ms
        bar_w = int(self.width * max(0.0, min(1.0, ratio)))
        bar_h = 5
        y = self.height - bar_h
        
        frame_np[y:self.height, 0:self.width] = [100, 100, 100]
        frame_np[y:self.height, 0:bar_w] = [0, 200, 0]

    def get_frame_at(self, timestamp_sec: float, chunk_start_ms: float = 0) -> np.ndarray:
        """Returns a numpy array (RGB) representing the frame at the given timestamp."""
        if not self._pre_rendered_frames:
            self.prepare_static_base()
            
        timestamp_ms = (timestamp_sec * 1000) + chunk_start_ms
        
        active_idx = -1
        for i, line in enumerate(self.renderable_lines):
            start_ms = line.get("start_ms")
            end_ms = line.get("end_ms")
            if start_ms is not None and end_ms is not None:
                if start_ms <= timestamp_ms <= end_ms:
                    active_idx = i
                    break
        
        frame = self._pre_rendered_frames.get(active_idx, self._pre_rendered_frames[-1]).copy()
        self._draw_progress_bar_numpy(frame, timestamp_ms)
        return frame
