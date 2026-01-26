# Plan: Mushaf Layout Data Analysis

This track involves investigating the schema and data alignment between `word_by_word_qpc-v2.db` and `qpc-v2-15-lines.db` to enable a 15-line Mushaf view.

## Phase 1: Database Investigation [checkpoint: cf28f26]
- [x] Task: Create a script to inspect and document the schemas of both databases.
    - [x] Sub-task: Write unit tests for the schema inspection utility (e.g., ensuring it can connect and list tables).
    - [x] Sub-task: Implement the inspection utility using `sqlite3`.
    - [x] Sub-task: Run the utility and record the table structures and column types in a markdown report.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Database Investigation' (Protocol in workflow.md) cf28f26

## Phase 2: Logic Development & Prototype
- [x] Task: Develop the matching logic to align words with line boundaries. ab2b41f
    - [x] Sub-task: Write TDD test cases for the matching utility (e.g., mocking small DB subsets).
    - [x] Sub-task: Implement the logic using `word_by_word_qpc-v2.db` for content and `qpc-v2-15-lines.db` for structure.
- [x] Task: Create a Python demonstration utility to output a sample layout. ab2b41f
    - [x] Sub-task: Implement a script that outputs JSON/Text showing Surah 1 (or Page 1) aligned by line.
    - [x] Sub-task: Enhance the script to generate a sample image of the page using `Pillow` or `opencv`, rendering the Arabic text line by line.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Logic Development & Prototype' (Protocol in workflow.md) a8ea580

## Phase 3: Final Analysis & Reporting [checkpoint: e7eae05]
- [x] Task: Conduct a full-Quran analysis to identify potential edge cases or data gaps.
- [x] Task: Finalize the technical report with join strategies and join keys.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Analysis & Reporting' (Protocol in workflow.md) e7eae05
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Analysis & Reporting' (Protocol in workflow.md)
