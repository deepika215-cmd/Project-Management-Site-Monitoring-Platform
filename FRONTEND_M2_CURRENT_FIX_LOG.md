# BuildTrack Milestone 1-2 Current Frontend Fix Log

This package is based on the latest Milestone 1-2 frontend/integration package. Backend business logic was not changed for these fixes.

## Fixed in this package
- Project Details now resolves the selected project from the persisted project list first, preventing the `/projects/project-details/:id` page from being trapped on the loading state when the single-project request is slow.
- Edit Project uses the persisted project list first for the same reason.
- Profile update and password-change requests now send the authenticated Bearer token.
- Profile has an 8-second live-request timeout and a cached authenticated-user fallback.
- User Management now uses the same shared BuildTrack sidebar/layout.
- Shared sidebar has an exact 235px width, hidden horizontal overflow, and a bottom navigation area so Logout remains reachable without page scrolling.
- Duplicate 235px content offsets were removed from pages that already reserve the shared sidebar width.
- Admin users can access Create Project because the existing route already permits ADMIN and PROJECT_MANAGER.
- Project Status no longer silently selects the first project when no project was requested; the user can explicitly select a project, while project-detail links still preselect the correct project through `projectId`.

## Scope
Frontend and frontend/backend integration only through Milestone 2. Existing backend API files are retained for the required local integration environment; no new backend business functionality was added by this fix pass.
