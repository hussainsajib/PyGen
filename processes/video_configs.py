RECITER="ar.alafasy"
FONT_COLOR = "black"
BACKGROUND = "background/mountains.jpg"
TARGET_HEIGHT = 1080
TARGET_WIDTH = 1920
MAIN_BOXES_HEIGHT = None
MAIN_BOXES_WIDTH = 1600
MAIN_TEXT_BOXES_SIZE=(MAIN_BOXES_WIDTH, MAIN_BOXES_HEIGHT)
ARABIC_TEXT_CLIP_POS = ('center', (TARGET_HEIGHT // 2) - 450)
TRANS_TEXT_CLIP_POS = ('center', (TARGET_HEIGHT // 2) + 50)
FOOTER_CONFIG = {
    "fontsize": 30, 
    "color": FONT_COLOR
}
TRANSLATON_TEXT_BOX_CONFIG = {
    "fontsize": 40, 
    "color": FONT_COLOR, 
    "font": 'Kalpurush', 
    "method": 'caption', 
    "size": MAIN_TEXT_BOXES_SIZE,
    "interline": 4
}
ARABIC_TEXT_BOX_CONFIG = {
    "fontsize": 65, 
    "color": FONT_COLOR, 
    "method": 'caption', 
    "size": MAIN_TEXT_BOXES_SIZE,
    "font": "KFGQPC Uthmanic Script Regular",
    "interline": 4
}
INTRO_DURATION = 4