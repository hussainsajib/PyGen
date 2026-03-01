import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
from factories.font_utils import resolve_font_path
from factories.shaping_utils import render_shaped_text
from bangla import convert_english_digit_to_bangla_digit as e2b
from config_manager import config_manager

class ImageGenerator:
    def __init__(self, width=1080, height=1080):
        self.width = width
        self.height = height
        self.canvas = Image.new("RGBA", (self.width, self.height), color=(255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.canvas)
        
        # Load default fonts
        self.bangla_font_name = config_manager.get("DEFAULT_BANGLA_FONT", "SolaimanLipi")
        self.bangla_font_path = resolve_font_path(self.bangla_font_name)
        
        # Fallback for Bangla font if not resolved correctly to a file that exists
        if not os.path.exists(self.bangla_font_path):
            fallback_paths = [
                r"C:\Windows\Fonts\Nirmala.ttc",
                r"C:\Windows\Fonts\Vrinda.ttf",
                "Arial.ttf" # Last resort
            ]
            for path in fallback_paths:
                if os.path.exists(path):
                    self.bangla_font_path = path
                    break

    def set_background(self, image_path, dim_opacity=0.5):
        """Sets the background image and applies a dimming layer."""
        if not os.path.exists(image_path):
            print(f"Warning: Background image not found at {image_path}")
            return
            
        bg = Image.open(image_path).convert("RGB")
        # Resize to cover the canvas
        bg_width, bg_height = bg.size
        aspect = bg_width / bg_height
        canvas_aspect = self.width / self.height
        
        if aspect > canvas_aspect:
            # Image is wider than canvas
            new_height = self.height
            new_width = int(new_height * aspect)
        else:
            # Image is taller than canvas
            new_width = self.width
            new_height = int(new_width / aspect)
            
        bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop
        left = (new_width - self.width) / 2
        top = (new_height - self.height) / 2
        right = (new_width + self.width) / 2
        bottom = (new_height + self.height) / 2
        bg = bg.crop((left, top, right, bottom))
        
        self.canvas.paste(bg, (0, 0))
        
        # Apply dimming
        if dim_opacity > 0:
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, int(255 * dim_opacity)))
            self.canvas.paste(overlay, (0, 0), overlay)
            self.draw = ImageDraw.Draw(self.canvas)

    def render_arabic_ayah(self, words, page_number, font_size=60, y_pos=200):
        """Renders Arabic text using QPC v2 page-specific font."""
        font_file = f"p{page_number}.ttf"
        font_path = os.path.join("QPC_V2_Font.ttf", font_file)
        
        if not os.path.exists(font_path):
            print(f"Warning: QPC v2 font not found at {font_path}")
            return 0
            
        font = ImageFont.truetype(font_path, font_size)
        
        # Concatenate and reverse for RTL
        text = "".join(words)[::-1]
        
        # Calculate text size using getbbox
        bbox = self.draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center horizontally
        x_pos = (self.width - text_width) / 2
        self.draw.text((x_pos, y_pos), text, font=font, fill=(255, 255, 255))
        
        return text_height

    def render_bangla_translation(self, text, font_size=40, y_pos=400):
        """Renders Bangla translation text using manual shaping."""
        shaped_img = render_shaped_text(text, self.bangla_font_path, font_size, (255, 255, 255))
        if not shaped_img:
            # Fallback to standard Pillow (may have ordering issues)
            font = ImageFont.truetype(self.bangla_font_path, font_size)
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = (self.width - text_width) / 2
            self.draw.text((x_pos, y_pos), text, font=font, fill=(255, 255, 255))
            return bbox[3] - bbox[1]
            
        x_pos = (self.width - shaped_img.width) // 2
        self.canvas.alpha_composite(shaped_img, (x_pos, y_pos))
        return shaped_img.height

    def render_metadata(self, surah_name, ayah_number, font_size=30, y_pos=600):
        """Renders localized metadata (Surah Name:Ayah Number)."""
        text = f"{surah_name}:{e2b(str(ayah_number))}"
        shaped_img = render_shaped_text(text, self.bangla_font_path, font_size, (200, 200, 200))
        
        if not shaped_img:
            font = ImageFont.truetype(self.bangla_font_path, font_size)
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = (self.width - text_width) / 2
            self.draw.text((x_pos, y_pos), text, font=font, fill=(200, 200, 200))
            return bbox[3] - bbox[1]
            
        x_pos = (self.width - shaped_img.width) // 2
        self.canvas.alpha_composite(shaped_img, (x_pos, y_pos))
        return shaped_img.height

    def render_branding(self, text="তাকওয়া বাংলা", font_size=25):
        """Renders branding watermark in the bottom-right corner."""
        shaped_img = render_shaped_text(text, self.bangla_font_path, font_size, (255, 255, 255))
        
        if not shaped_img:
            font = ImageFont.truetype(self.bangla_font_path, font_size)
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_pos = self.width - text_width - 40
            y_pos = self.height - text_height - 40
            self.draw.text((x_pos, y_pos), text, font=font, fill=(255, 255, 255))
            return
            
        x_pos = self.width - shaped_img.width - 40
        y_pos = self.height - shaped_img.height - 40
        self.canvas.alpha_composite(shaped_img, (x_pos, y_pos))

    def save(self, output_path):
        """Saves the final image."""
        # Convert to RGB before saving to avoid alpha channel issues in some viewers
        final_img = self.canvas.convert("RGB")
        final_img.save(output_path)
