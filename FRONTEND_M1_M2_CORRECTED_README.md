# BuildTrack — Milestone 1–2 Frontend + Backend Integration (Corrected)

This package is based on the latest `BuildTrack-Milestone1-2-FRONTEND-INTEGRATION-CORRECTED.zip` and is intended for the **frontend + frontend/backend integration work only through Milestone 2**.

## What was corrected

- Reworked Create Project UI and validation.
- Create Project now uses the authenticated user as `manager_id` and redirects to the project list after a successful POST.
- Project List reloads from FastAPI after creation and supports refresh, search, filters, view, edit and delete.
- Project Details has retry/error handling, tracking, milestone information and direct links to the selected project's status/milestones.
- Edit Project validates dates/budget and saves through the existing PUT endpoint.
- Project Status now follows the backend's valid lifecycle transitions and supports project-specific deep links.
- Milestones now support project-specific deep links and a proper modal-style Add Milestone form while retaining real CRUD calls.
- Frontend API base URL is `http://localhost:8000`, matching the local FastAPI/CORS configuration.
- No new backend endpoints were invented and the existing backend architecture was not replaced.

## Start the backend first

Open PowerShell in the **backend** folder, not the repository root:

```powershell
cd "C:\path\to\Project-Management-Site-Monitoring-Platform-main\backend"
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Keep that terminal running.

## Start the frontend

Open a second PowerShell:

```powershell
cd "C:\path\to\Project-Management-Site-Monitoring-Platform-main\frontend"
npm install
ng serve
```

Open:

`http://localhost:4200`

## Important database note

The backend currently uses a relative SQLite URL (`sqlite:///./buildtrack.db`). Therefore, start Uvicorn from the **backend folder** so the intended `backend/buildtrack.db` is used.

Do not delete the existing database if you need its current data.

## Milestone 2 test order

1. Login / authentication
2. User Management
3. Project List
4. Create Project
5. Refresh Project List and verify the created project remains
6. Project Details
7. Edit Project and refresh to verify persistence
8. Delete Project and refresh to verify deletion
9. Add Milestone
10. Edit Milestone
11. Delete Milestone
12. Project Status transition
13. Project Tracking

## Verification limitation

The source was checked for TypeScript syntax and the edited templates were structurally reviewed. A full Angular production build could not be run in the preparation environment because the npm registry available there returned a 404 for one dependency tarball. Therefore, do not treat this package as a claim that your local `ng build` has already passed; run `npm install` and `ng build` locally.
