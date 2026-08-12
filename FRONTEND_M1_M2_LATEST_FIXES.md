# BuildTrack Milestone 1-2 Frontend + Integration Fixes

This package continues from the latest `BuildTrack-Milestone1-2-FRONTEND-INTEGRATION-FIXED-LATEST.zip`.

## Frontend fixes in this revision

- Replaced the duplicated project-module sidebars with one shared fixed BuildTrack sidebar.
- Sidebar now stays fixed on desktop and keeps Logout accessible without scrolling through the dashboard.
- Sidebar Dashboard link is role-aware using the authenticated user's cached role.
  - ADMIN -> Admin Dashboard
  - PROJECT_MANAGER -> Project Manager Dashboard
  - SITE_ENGINEER -> Site Engineer Dashboard
  - CONTRACTOR -> Contractor Dashboard
  - WORKER -> Worker Dashboard
  - CLIENT -> Client Dashboard
- Project List Refresh now clears stale filters and reloads persisted backend records.
- Project List View/Edit actions now use explicit Angular navigation handlers instead of relying only on anchor navigation.
- Project List action buttons have consistent styling.
- Added the missing `On Hold` status option to the project filter.
- Milestone Edit/Delete/Save/Cancel buttons are explicitly non-submit buttons so they cannot accidentally trigger form submission.
- Profile page rebuilt to use the same BuildTrack page shell, cards, spacing, buttons and fixed sidebar as the project pages.
- Profile Refresh, Edit Profile, Save Profile, Change Password and Logout are connected to the existing frontend API integration.
- Updated `currentUser` in localStorage after a successful profile update so role-aware navigation stays in sync.
- Project create, milestone management, project status and project edit routes are restricted to ADMIN and PROJECT_MANAGER on the frontend.
- Project details remains available to authenticated users.

## Backend scope

No backend source code was intentionally changed in this revision. The frontend continues to call the existing FastAPI endpoints already present in the package.

## Important test commands

Frontend:

```powershell
cd frontend
npm install
ng serve
```

Backend (from the repository root, with the backend virtual environment activated):

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend `requirements.txt` is inside the `backend` folder, not the repository root.
