# Implementation Plan - Bengali Localization for Juz Videos

## Phase 1: Core Localization (Engine & Data)
Update the video generation engines to use the "Para" label for Juz videos in Bengali.

- [ ] Task: Update `processes/mushaf_video.py` (`generate_juz_video`) to use `পারা [Bengali Digit]` when the current language is Bengali.
- [ ] Task: Update `processes/mushaf_fast_video.py` (`generate_mushaf_fast`) to apply the same label change for high-speed Juz videos.
- [ ] Task: Create a unit test `tests/test_juz_label_bengali.py` to verify the logic for generating the Para label.
- [ ] Task: Conductor - User Manual Verification 'Core Localization (Engine & Data)' (Protocol in workflow.md)

## Phase 2: Metadata & Descriptions
Update the metadata generation logic for social media platforms.

- [ ] Task: Update `processes/description.py` (`generate_juz_details`) to use the new Bengali title format: `কুরআন তিলাওয়াত - পারা [Bengali Number] - [Bengali Reciter Name]`.
- [ ] Task: Ensure the description content in `generate_juz_details` also uses "পারা" instead of "Juz".
- [ ] Task: Verify the generated `.txt` metadata files for a sample Juz video.
- [ ] Task: Conductor - User Manual Verification 'Metadata & Descriptions' (Protocol in workflow.md)

## Phase 3: Integration & Final Verification
Ensure end-to-end consistency.

- [ ] Task: Generate a sample Juz 1 Mushaf video (or a few frames) and verify the footer text visually.
- [ ] Task: Synchronize `conductor/product.md` to reflect the improved Bengali localization for Juz videos.
- [ ] Task: Conductor - User Manual Verification 'Integration & Final Verification' (Protocol in workflow.md)
