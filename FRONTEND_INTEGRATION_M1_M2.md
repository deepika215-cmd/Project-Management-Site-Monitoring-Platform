# BuildTrack – Frontend + Existing Backend Integration (Milestones 1–2)

This version is intentionally scoped to the user's responsibility: **Angular frontend work and integration with the existing FastAPI backend**.

## Backend policy

The backend source was preserved from the supplied project ZIP. No FastAPI routes, SQLAlchemy models, Pydantic schemas, database files, authentication implementation, or backend configuration were changed.

## Frontend work included

- Replaced the mock-only ProjectService with API-backed project operations.
- Connected project list, create, details, update, status, closure and tracking screens to existing FastAPI endpoints.
- Connected milestones CRUD to the existing `/milestones/` API.
- Connected resource allocation/release/utilization to existing resource APIs and corrected the release request body.
- Added frontend Inventory and Workforce/Attendance screens using the existing backend APIs.
- Removed frontend calls to worker/attendance/procurement endpoints that do not exist in the supplied backend.
- Added JWT expiry checking and an Admin role guard for User Management.
- Cached the authenticated user after login for frontend role checks.
- Added route aliases for existing navigation links that pointed to old frontend paths.
- Added frontend-only error/loading/empty states in the touched modules.

## Backend endpoints intentionally used

- `/auth/*`
- `/users/*`
- `/projects/*`
- `/milestones/*`
- `/resources/*`
- `/inventory/*`
- `/workers/*`
- `/attendance/*`

No `/site-progress` API was invented because it is not present in the supplied backend.

## Verification

- Backend source comparison against the supplied ZIP: **unchanged**.
- Changed frontend TypeScript files were checked with the available TypeScript compiler for project-level errors; Angular package modules were unavailable because `npm ci` could not complete in this environment.
- Full `ng build` was **not claimed as PASS** because dependency installation failed with an npm registry 404 for `zod-to-json-schema@3.25.2` in the execution environment.

## Windows commands

From the extracted project root:

```powershell
cd frontend
npm install
npm start
```

In another PowerShell window:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

If the virtual environment does not exist yet:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:4200`.
