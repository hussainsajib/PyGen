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

## Analysis & Hypothesis
The `qpc-v2-15-lines.db` seems to define line boundaries using `first_word_id` and `last_word_id`. If these IDs correspond to the `id` column in `word_by_word_qpc-v2.db`, then the mapping strategy is straightforward:
1. Iterate through `pages` table in 15-Line DB.
2. For each line, fetch words from `word_by_word_qpc-v2.db` where `id` is between `first_word_id` and `last_word_id`.

This needs validation in the next phase.
