# Auto-refresh and Resource Management frontend fixes

## Scope
Frontend-only changes. No backend source files were modified.

## 1. Automatic UI refresh
Added `frontend/src/app/interceptors/ui-refresh-interceptor.ts` and registered it in `frontend/src/app/app.config.ts`.

The current Angular app is standalone and does not load `zone.js`. Existing pages update normal component properties inside `HttpClient` subscriptions, so the browser could show new data only after another UI event (such as a click) or a full refresh. The interceptor runs an Angular application change-detection check after HTTP requests complete, so existing pages can update immediately without rewriting every page.

## 2. Resource Management Add button
Updated `frontend/src/app/pages/resources/resource-allocation/resource-allocation.html`, `.ts`, and `.css`.

Added:
- `+ Add Resource` button in the page header
- Add Resource modal/form
- Resource name
- Category/type
- Quantity
- Status
- Project selection
- Save/cancel behavior
- Existing backend `POST /resources/` integration through `Api.createResource()`
- Immediate table refresh after successful creation

Also added Edit, Maintenance, and Available actions so the existing backend update endpoint can be used from the same page.

## 3. Backend
No backend files were changed. The current backend requires `project_id` when creating/updating a resource, so the form loads the existing projects and requires a project selection.

## 4. Testing
A full Angular build was not run in this environment because the supplied project does not include `node_modules`. After extracting the ZIP, run `npm install` in `frontend`, then `npx ng serve`.
