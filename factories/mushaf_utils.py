def assemble_mushaf_line_text(words: list) -> str:
    """
    Concatenates words for a Mushaf line and reverses the entire string
    to correctly handle RTL rendering on LTR canvases (e.g. Pillow).
    This ensures multi-glyph visual units (like words with pause signs) 
    maintain their correct internal sequence while the line flows RTL.
    """
    if not words:
        return ""
    # Join logically (W1+W2+W3) then reverse everything (reverse(W3)+reverse(W2)+reverse(W1))
    return "".join([w["text"] for w in words])[::-1]
