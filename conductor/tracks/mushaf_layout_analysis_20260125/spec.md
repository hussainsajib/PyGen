# Specification: Mushaf Layout Data Analysis

## Overview
This track aims to analyze two key databases—`word_by_word_qpc-v2.db` and `qpc-v2-15-lines.db`—to establish a mapping strategy for generating a "Mushaf-like" view (specifically a 15-line layout) for users. The goal is to determine how individual words from the Word-by-Word DB can be grouped and aligned according to the line and page markings in the 15-Line DB.

## Functional Requirements

### 1. Database Schema Investigation
- Analyze the tables and columns in `word_by_word_qpc-v2.db` to identify word text, Surah, and Ayah identifiers.
- Analyze the tables and columns in `qpc-v2-15-lines.db` to identify page numbers, line numbers, and the corresponding text strings or identifiers that mark line boundaries.

### 2. Matching Strategy
- Develop a logic to "join" or map these two datasets.
- Use `qpc-v2-15-lines.db` as the source of truth for **structure** (where lines and pages begin/end).
- Use `word_by_word_qpc-v2.db` as the source of truth for the **content** (individual Arabic words and metadata).

### 3. Demonstration Script (Python)
- Create a Python utility that:
    - Connects to both SQLite databases.
    - Performs a sample mapping for a specific range (e.g., a specific Surah or Page).
    - Outputs a structured representation (e.g., JSON or a formatted text list) showing words grouped by Page and Line.
    - **Visual Output:** Generates a sample image of the requested page (e.g., `page_1.png`) by rendering the text line-by-line using a standard Arabic font (e.g., `me_quran.ttf` or similar available in the project).

## Data Points to be Extracted
- From 15-Line DB: `page_number`, `line_number`, and `line_text` (for alignment check).
- From Word-by-Word DB: `word_arabic_text`, `surah_number`, `ayah_number`, and `word_id`/`position`.

## Non-Functional Requirements
- **Performance:** The matching script should be efficient enough to process the entire Quran in a reasonable time if needed.
- **Clarity:** The final analysis report must be clear and reproducible.

## Acceptance Criteria
- [ ] Successful extraction of schemas from both databases.
- [ ] A validated matching logic that correctly groups words into the 15-line format.
- [ ] A Python script demonstrating the logic by outputting a sample page/line view.
- [ ] Final report identifying any edge cases (e.g., words spanning lines if applicable, though source-of-truth assumptions minimize this).

## Out of Scope
- Implementing the actual frontend view.
- Migrating data into a new unified database (this is an analysis phase).
- Correcting errors in the source databases (only identifying them).
