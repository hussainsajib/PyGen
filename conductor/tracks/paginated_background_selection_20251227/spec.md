# Track Specification: Paginated Background Selection

## Overview
This track enhances the background selection interface by increasing the number of loaded Unsplash images from 10 to 20 per set and introducing pagination. Users will be able to navigate through multiple pages of search results using "Previous" and "Next" buttons, providing a richer selection of visuals for video backgrounds.

## Functional Requirements
- **Increased Result Limit:** Update the image search logic to fetch and display 20 images per request.
- **Pagination Navigation:**
    - Add "Previous" and "Next" buttons within the background selection modal.
    - **Visibility:** 
        - The "Previous" button is hidden on the first page.
        - The "Next" button is always visible as long as results are returned.
    - **Logic:** Each button click triggers a new request to the backend with the updated page index.
- **UI Feedback:**
    - Display a loading spinner while fetching new pages.
    - Automatically scroll the modal content to the top when a new page is loaded.
    - Display a "Page X" indicator for user context.
- **Unified Interface:** Ensure the new paginated logic works identically on both the root index (`/`) and the `/word-by-word` interfaces.

## Technical Requirements
- **Backend API:**
    - Update the `/unsplash-search` route in `app.py` to accept a `page` parameter (defaulting to 1).
    - Update `net_ops/unsplash.py` to pass the `per_page` (set to 20) and `page` parameters to the Unsplash API.
- **Frontend Logic:**
    - Update the `searchUnsplash` JavaScript function in `index.html` and `wbw.html` to maintain state for the current `currentPage`.
    - Implement `nextPage` and `prevPage` functions to increment/decrement the counter and re-trigger the search.
    - Integrate the navigation buttons into the modal layout.

## Acceptance Criteria
- [ ] Searching for backgrounds returns 20 images instead of 10.
- [ ] Navigation buttons appear correctly and allow moving between sets of 20 images.
- [ ] The "Previous" button is correctly hidden on Page 1.
- [ ] Loading indicators and scroll-to-top behavior function as expected.
- [ ] Selection of an image from any page correctly sets the active background.

## Out of Scope
- Displaying total page counts (since Unsplash search results can be dynamic).
- Jump-to-page functionality.
