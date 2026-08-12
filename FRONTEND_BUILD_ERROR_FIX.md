# Frontend Build Error Fix

The previous frontend ZIP had Angular HttpClient methods without response type parameters. Angular inferred `Observable<Object>`, which caused TS2696/TS2769 errors when array-based pages assigned the response to `any[]`.

## Fix

`frontend/src/app/services/api.ts` now explicitly types collection endpoints as `Observable<any[]>` through `HttpClient.get<any[]>`, while singular/mutation endpoints use `any`.

Affected collection endpoints:
- GET /users/
- GET /projects/
- GET /milestones/
- GET /resources/
- GET /inventory/
- GET /workers/
- GET /attendance/
- GET /procurement/
- GET /notification/
- GET /report/

No backend files were changed.

## Run on Windows PowerShell

```powershell
cd frontend
npm install
ng serve
```

If the backend is needed:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```
