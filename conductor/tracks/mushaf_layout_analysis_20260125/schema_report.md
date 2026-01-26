# Database Schema Analysis

## Overview
This report documents the schemas of `word_by_word_qpc-v2.db` and `qpc-v2-15-lines.db` extracted using the schema inspection utility.

## 1. Word-by-Word Database (`word_by_word_qpc-v2.db`)

**Table: `words`**
- `id` (INTEGER): Likely a unique identifier for the word (global).
- `location` (TEXT): A location string (possibly "surah:ayah:word").
- `surah` (INTEGER): Surah number.
- `ayah` (INTEGER): Ayah number.
- `word` (INTEGER): Word position within the Ayah.
- `text` (TEXT): The Arabic text of the word.

## 2. 15-Line Database (`qpc-v2-15-lines.db`)

**Table: `pages`**
- `page_number` (INTEGER): The page number in the Mushaf (1-604).
- `line_number` (INTEGER): The line number on the page (1-15).
- `line_type` (TEXT): Type of line (e.g., "start_sura", "ayah", "bismillah").
- `is_centered` (INTEGER): Boolean flag?
- `first_word_id` (INTEGER): ID of the first word on this line (likely maps to `word_by_word_qpc-v2.db`'s `id`?).
- `last_word_id` (INTEGER): ID of the last word on this line.
- `surah_number` (INTEGER): Surah number (for context).

**Table: `info`**
- General metadata about the Mushaf (pages, lines/page, font).

## Analysis & Validation Results
A full analysis of all 604 pages was conducted using `scripts/full_analysis.py`.

### Key Findings
- **Data Consistency:** 100% of the words in `word_by_word_qpc-v2.db` (83,668 words) are perfectly mapped to the line boundaries defined in `qpc-v2-15-lines.db`.
- **Anomalies:** 0 anomalies were found. Every line of type 'ayah' or 'basmallah' has a valid range of word IDs.
- **Line Types:**
    - `surah_name`: 114 occurrences (one per Surah).
    - `basmallah`: 112 occurrences.
    - `ayah`: 8,820 occurrences.

### Join Strategy
To generate a Mushaf-like view:
1.  **Source of Structure:** Query `pages` table in `qpc-v2-15-lines.db`.
2.  **Join Key:** Use `pages.first_word_id` and `pages.last_word_id` to query the `words` table in `word_by_word_qpc-v2.db`.
3.  **Rendering Font:** Use the page-specific `.ttf` file from the `QPC_V2_Font.ttf` folder (e.g., `p1.ttf` for page 1).
4.  **Bidi Handling:** Since Mushaf text is RTL, reverse the list of words for each line before rendering in LTR-based engines (like standard Pillow).

### Prototype Utility
The prototype `scripts/mushaf_mapper.py` successfully demonstrates this strategy by generating accurate PNG images of Mushaf pages.

