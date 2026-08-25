# BuildTrack — Frontend + Backend Integration (Milestones 1–2)

This update is **frontend-focused**. The existing FastAPI backend architecture was preserved and no backend source files were changed by this frontend correction pass.

## Important: start the backend from `backend`

The current backend uses a relative SQLite URL (`sqlite:///./buildtrack.db`). Start Uvicorn from the `backend` folder so it uses `backend/buildtrack.db` consistently.

### Terminal 1 — Backend

```powershell
cd "C:\path\to\Project-Management-Site-Monitoring-Platform-main\backend"
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Swagger should be available at `http://127.0.0.1:8000/docs`.

### Terminal 2 — Frontend

```powershell
cd "C:\path\to\Project-Management-Site-Monitoring-Platform-main\frontend"
npm install
ng serve
```

Open `http://localhost:4200`.

## Project Management test flow

1. Log in.
2. Open **Projects**.
3. Click **Create Project**.
4. Enter name, location, start/end date, budget and description.
5. Confirm the Manager ID is the authenticated user's ID.
6. Click **Create Project**.
7. Confirm the success message appears.
8. Confirm the project details page opens.
9. Go back to **Projects** and refresh. The project must still appear.
10. Open **Edit** and save a change. Refresh and confirm it persists.
11. Open **Milestones**, select the project and create a milestone. Refresh and confirm it persists.
12. Open **Status** and select the project. Confirm tracking is loaded.
13. Change status only through a valid lifecycle transition: Planning → In Progress → Completed → Closed.
14. Return to project details and confirm progress reflects completed milestones.
15. Delete the project from the list or details page and confirm it disappears after refresh.

## If Create Project fails

Do not assume the frontend is the problem. Read the red error message on the page. Common causes are:

- Backend is not running on port 8000.
- The logged-in user's ID does not exist in the database being used by Uvicorn.
- Uvicorn was started from the repository root, creating/using a different `buildtrack.db` because the backend database URL is relative.
- Start Uvicorn from `backend` as shown above.

## What was corrected in this pass

- Reworked the Create Project UI so all fields are properly styled and responsive.
- Uses the authenticated backend user to populate Manager ID when available.
- Added clear validation, loading, success and API error states.
- Improved Project Status UI and empty-project handling.
- Improved Milestone creation/edit/delete UI and empty states.
- Added Project Details tracking section.
- Added Edit Project UI improvements.
- Added Delete Project actions from the project list and details page.
- Preserved the existing Angular services and FastAPI endpoints rather than inventing new APIs.
