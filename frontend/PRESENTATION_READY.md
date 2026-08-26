# BuildTrack – Presentation Ready Fixes

## What was fixed
- Resource Allocation now uses the shared BuildTrack sidebar.
- Resource Allocation UI was redesigned with responsive cards, filters, utilization, allocation/release actions and equipment categories.
- Site Progress Monitoring now uses the shared sidebar.
- Site Progress page now includes daily reports, weekly report count, progress/milestone status, delay tracking and site activity history.
- Site Progress works in demo mode using browser localStorage if the backend does not expose `/site-progress/`; when that endpoint exists, API data is used.
- Added Site Engineer navigation to the shared sidebar.

## Run the frontend on Windows
Use Node 22 LTS for the Angular 22 project. Node 24 is not recommended for this project.

```powershell
cd frontend
npm install
npx ng serve
```

If `ng serve` reports a broken Angular installation:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install
npx ng serve
```

Then open http://localhost:4200.

## Backend
Start the existing backend separately:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

The frontend does not replace or modify the supplied backend APIs.
