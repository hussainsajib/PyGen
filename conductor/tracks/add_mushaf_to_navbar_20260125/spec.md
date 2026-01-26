# Specification: Add Mushaf to Navbar

## Overview
This track involves adding a direct link to the newly created Mushaf Viewer (`/mushaf`) in the global navigation bar. This will ensure that users can easily access the traditional Mushaf layout from any page in the application.

## Functional Requirements

### 1. Navbar Update
- Modify `templates/base.html` to include a new navigation item.
- **Link Text:** "Mushaf"
- **Destination:** `/mushaf` (using `url_for('mushaf')`)
- **Placement:** At the end of the existing navigation list, immediately following the "Manual Upload" link.
- **Styling:** Must match the CSS classes used for existing navbar links (`nav-item`, `nav-link`) to maintain visual consistency.

## Acceptance Criteria
- [ ] A "Mushaf" link is visible in the navbar on all pages.
- [ ] Clicking the "Mushaf" link correctly navigates the user to the Mushaf Viewer page.
- [ ] The link follows the same hover and active states as other navigation items.

## Out of Scope
- Adding icons to the navbar links.
- Reorganizing the entire navigation structure.
