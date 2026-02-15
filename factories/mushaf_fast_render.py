import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from factories.video import get_resolution
from processes.video_configs import BACKGROUND_OPACITY, BACKGROUND_RGB, FONT_COLOR
from config_manager import config_manager

# Import necessary constants and logic from single_clip or redefine them here if needed
# To avoid circular imports, I'll redefine some shared logic or move them to a common util later

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
    def __init__(self, page_number: int, is_short: bool, lines: list, font_scale: float = 0.8, background_input: str = None):
        self.page_number = page_number
        self.is_short = is_short
        self.lines = lines
        self.font_scale = font_scale
        self.background_input = background_input
        self.resolution = get_resolution(is_short)
        self.width, self.height = self.resolution
        
        self.font_paths = {
            "page": os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page_number}.ttf")),
            "bsml": os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF")),
            "sura": os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf"))
        }
        if not os.path.exists(self.font_paths["page"]):
            self.font_paths["page"] = "Arial"

        self.line_height = (self.height * 0.8) / 15
        self.static_base = None
        self.renderable_lines = []
        self.line_positions = []
        
        # Prepare content data
        self._prepare_renderable_lines()

    def _prepare_renderable_lines(self):
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

    def prepare_static_base(self):
        """Renders the background, border, and static text once."""
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

    def get_frame_at(self, timestamp_sec: float) -> np.ndarray:
        """Returns a numpy array (RGB) representing the frame at the given timestamp."""
        if self.static_base is None:
            self.prepare_static_base()
            
        timestamp_ms = timestamp_sec * 1000
        img = self.static_base.copy()
        draw = ImageDraw.Draw(img, 'RGBA')
        
        highlight_color = (255, 255, 0, 76) # Yellow with 0.3 opacity (approx 76/255)
        
        for i, line in enumerate(self.renderable_lines):
            l_type = line.get("line_type", "ayah")
            if l_type in ["basmallah", "surah_name"]:
                continue
                
            start_ms = line.get("start_ms")
            end_ms = line.get("end_ms")
            
            if start_ms is not None and end_ms is not None:
                if start_ms <= timestamp_ms <= end_ms:
                    # Calculate highlight width
                    from factories.single_clip import calculate_mushaf_font_size
                    words = line.get("words", [])
                    text = "".join([w["text"] for w in reversed(words)])
                    font_size = calculate_mushaf_font_size(self.width, self.line_height, l_type, self.font_scale)
                    
                    cache_key = f"{self.font_paths['page']}_{font_size}"
                    if cache_key not in FONT_CACHE:
                        FONT_CACHE[cache_key] = ImageFont.truetype(self.font_paths['page'], font_size)
                    font = FONT_CACHE[cache_key]
                    
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_w = bbox[2] - bbox[0]
                    h_width = text_w + 20
                    
                    y_pos = self.line_positions[i]
                    x0 = (self.width - h_width) // 2
                    y0 = y_pos
                    x1 = x0 + h_width
                    y1 = y0 + int(self.line_height)
                    
                    # Draw semi-transparent rectangle
                    draw.rectangle([x0, y0, x1, y1], fill=highlight_color)
                    
        # Convert to RGB numpy array
        return np.array(img.convert('RGB'))
