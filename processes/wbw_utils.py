def segment_words_into_lines(words: list, translations: list, char_limit: int):
    """
    Groups words into lines/segments based on a soft character limit.
    Each segment includes the words and their corresponding translations.
    """
    segments = []
    current_segment_words = []
    current_segment_trans = []
    current_char_count = 0
    
    for i in range(len(words)):
        word = words[i]
        trans = translations[i] if i < len(translations) else ""
        
        current_segment_words.append(word)
        current_segment_trans.append(trans)
        
        # We use a soft limit: add the word, THEN check if we exceeded the limit
        # We also account for spaces between words (+1)
        current_char_count += len(word)
        
        if current_char_count >= char_limit:
            segments.append({
                "words": current_segment_words,
                "translations": current_segment_trans,
                "text": " ".join(current_segment_words),
                "translation_text": " ".join(current_segment_trans)
            })
            current_segment_words = []
            current_segment_trans = []
            current_char_count = 0
        else:
            # Add space for the next word
            current_char_count += 1
            
    # Add the last segment if not empty
    if current_segment_words:
        segments.append({
            "words": current_segment_words,
            "translations": current_segment_trans,
            "text": " ".join(current_segment_words),
            "translation_text": " ".join(current_segment_trans)
        })
        
    return segments

def segment_words_with_timestamps(words: list, translations: list, timestamps: list, char_limit: int, interlinear: bool = False, translation_ratio: float = 0.5):
    """
    Groups words into lines/segments and aggregates their collective timestamps.
    In interlinear mode, it accounts for the width of both Arabic and translation text.
    """
    segments = []
    current_segment_words = []
    current_segment_trans = []
    current_char_count = 0
    
    # Map word number to its timestamp
    time_map = {t[0]: (t[1], t[2]) for t in timestamps}
    
    segment_start_ms = None
    
    for i in range(len(words)):
        word = words[i]
        trans = translations[i] if i < len(translations) else ""
        word_num = i + 1
        
        # Get word timing
        word_times = time_map.get(word_num)
        if not word_times:
            continue
            
        if segment_start_ms is None:
            segment_start_ms = word_times[0]
            
        # Calculate effective width for this word block
        if interlinear:
            # We assume Bengali/translation characters are roughly half the width of Arabic characters
            # at the same font size, or we use the provided ratio.
            effective_width = max(len(word), len(trans) * translation_ratio)
        else:
            effective_width = len(word)

        current_segment_words.append(word)
        current_segment_trans.append(trans)
        current_char_count += effective_width
        
        # Final word or exceeded limit
        if current_char_count >= char_limit or i == len(words) - 1:
            segments.append({
                "words": current_segment_words,
                "translations": current_segment_trans,
                "text": " ".join(current_segment_words),
                "translation_text": " ".join(current_segment_trans),
                "start_ms": segment_start_ms,
                "end_ms": word_times[1]
            })
            current_segment_words = []
            current_segment_trans = []
            current_char_count = 0
            segment_start_ms = None
        else:
            # Add space for the next word
            current_char_count += 1
            
    # Flush remaining words if any
    if current_segment_words:
        segments.append({
            "words": current_segment_words,
            "translations": current_segment_trans,
            "text": " ".join(current_segment_words),
            "translation_text": " ".join(current_segment_trans),
            "start_ms": segment_start_ms,
            "end_ms": timestamps[-1][2] if timestamps else 0
        })

    return segments
