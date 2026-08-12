# BuildTrack — Latest Milestone 1–2 Frontend Fixes

Base used: `BuildTrack-Milestone1-2-FRONTEND-INTEGRATION-CORRECTED-FINAL.zip`

Scope: frontend + integration only. The backend source was not changed in this correction.

## Fixed
- Project List now reloads whenever the route/query parameters change, including after Create Project navigation.
- Project List now explicitly triggers Angular change detection after API responses, so persisted projects render immediately without needing to touch a filter.
- Refresh on Project List reloads projects and progress from FastAPI.
- Project Status now explicitly loads and refreshes tracking from `/projects/{id}/tracking`.
- Project Status has a tracking refresh control and a visible tracking-loading state.
- Milestone create/update/delete callbacks now reset loading state and refresh the visible list.
- Milestone create/delete show success feedback.
- Project-module shell dimensions are normalized across Project List, Create, Details, Update, Milestones and Status (same desktop sidebar width, content padding and heading sizing).

## Backend endpoints used
- `GET /projects/`
- `POST /projects/`
- `GET /projects/{id}`
- `PUT /projects/{id}`
- `DELETE /projects/{id}`
- `PUT /projects/{id}/status`
- `PUT /projects/{id}/close`
- `GET /projects/{id}/tracking`
- `GET /milestones/`
- `POST /milestones/`
- `PUT /milestones/{id}`
- `DELETE /milestones/{id}`

## Verification note
The source files were inspected after editing. A full Angular build was not run in this environment because the ZIP does not contain `node_modules`; local dependency installation/build should still be run with `npm install` and `ng build` on Windows.
