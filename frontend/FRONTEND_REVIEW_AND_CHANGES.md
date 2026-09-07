# BuildTrack Frontend Review and Changes

## Scope
Only the Angular frontend was modified. The FastAPI backend was inspected only to verify existing endpoints and request/response fields; no backend file was changed.

## Validation performed
- Angular/TypeScript compilation check with Angular compiler (`ngc --noEmit`) passed.
- A normal `ng build` could not be completed inside the Linux review container because the uploaded `node_modules` contains Windows esbuild binaries and the container Node version is below Angular 22's required patch version. Reinstall dependencies on the target machine (`npm ci`) before `npm run build`.

## Frontend files changed
- `src/app/app.routes.ts` — added Module 3/4 routes, tightened RBAC, made project creation Admin-only, protected workforce/inventory/procurement/report/analytics routes.
- `src/app/services/api.ts` — added frontend API bindings for daily/weekly progress, delays, machinery, maintenance, material lifecycle, stock movement, vendors, procurement requests, purchase orders and invoices.
- `src/app/shared/app-sidebar.component.html` — role-specific navigation aligned more closely with Administrator, Project Manager, Site Engineer, Contractor, Worker and Client responsibilities.
- `src/app/pages/site-progress/site-progress.ts|html|css` — new Module 3 screen for Daily Progress, Weekly Progress and Delay Tracking.
- `src/app/pages/resources/resource-operations/resource-operations.ts|html|css` — new Module 4 screen for Machinery Tracking, Availability, Utilization and Maintenance Scheduling.
- `src/app/pages/inventory/inventory.ts|html|css` — replaced incorrect inventory CRUD flow with the backend-supported Material → Stock Movement → Request → Allocation → Consumption lifecycle.
- `src/app/pages/procurement/procurement.ts|html|css` — expanded Module 7 to Procurement Requests, approvals, Vendor Management, Purchase Orders and Invoice Tracking.
- `src/app/pages/dashboards/contractor-dashboard/contractor-dashboard.ts|html` — removed inappropriate procurement workflow from Contractor dashboard and linked workforce/attendance/progress functions.
- `src/app/pages/dashboards/worker-dashboard/worker-dashboard.html` — removed direct Projects navigation and corrected worker notification route.
- `src/app/pages/dashboards/client-dashboard/client-dashboard.html` — corrected client notification route.

## Important corrections
1. The original Material Inventory UI called `POST/PUT/DELETE /inventory`, but the supplied backend exposes inventory as read-only and expects stock changes through Material and Stock Movement endpoints. The frontend now uses the backend-supported lifecycle.
2. The old Site Progress service called `/site-progress`, which is not an endpoint in the supplied backend. The new Module 3 screen uses `/daily-progress`, `/weekly-progress`, and `/delay-records`.
3. Resource Management previously redirected Equipment Tracking and Resource Utilization back to the allocation screen. Dedicated machinery/utilization/maintenance UI is now available.
4. Procurement previously used only the legacy `/procurement` CRUD endpoint. The main Module 7 screen now uses the richer `/procurement-requests`, `/vendors`, `/purchase-orders`, and `/invoices` workflow.
5. Project creation was accessible to Project Managers in the frontend. The requirement says only Administrator creates a project, so the route is now Admin-only.
6. Several navigation links allowed roles to reach modules outside their described responsibilities. The sidebar and routes were tightened.

## Still unfinished / backend-dependent from the specification
### Module 1
- Registration fields in the specification include Employee ID, Department/Designation, Address and optional Profile Picture. These depend on whether the backend user schema supports them.
- Full profile-picture upload is not demonstrated.

### Module 2
- Project history/audit trail for updates is not represented by a dedicated backend endpoint.
- Strict project-to-client, project-to-contractor and project-to-site-engineer assignment screens depend on backend relationship support.
- Closure validation (all milestones/inspections/financial settlement/client acceptance before close) is backend business logic and cannot be guaranteed from frontend alone.

### Module 3
- Daily, weekly and delay workflows are now wired to existing backend endpoints.
- A separate Site Activity Log entity/API is not present in the supplied backend.
- Photo metadata exists in the backend, but a complete binary photo upload/storage workflow is not established by the supplied API.
- Automatic weighted project completion and automatic milestone completion require backend business rules.

### Module 4
- Machinery tracking and maintenance are now exposed in the frontend.
- Resource allocation history with Allocation Date, Expected Return Date and Responsible Person is not represented by the current Resource schema.
- Maintenance reminders/notifications require notification integration/background scheduling.

### Module 5
- Material master, inventory status, requests, allocation, consumption and stock movements are wired to existing endpoints.
- Automatic conversion of shortage into a procurement request is not exposed as one complete backend workflow.
- Low-stock notifications require Module 8 integration.

### Module 6
- Worker CRUD and attendance exist.
- Contractor → Worker → Project assignment history is not represented by dedicated backend entities/APIs.
- Shift Scheduling is missing from the backend.
- Payroll Monitoring (pay rate, hours, overtime, estimated pay, payroll status) is missing from the backend.
- Bulk worker CSV/Excel registration is not provided by the current backend.

### Module 7
- Requests, approvals, vendors, purchase orders and invoices are now available in the frontend.
- Detailed Purchase Order Item / Procurement Request Item management should still be added for a full multi-item procurement workflow.
- A complete material-received → inventory-update user flow depends on PO items being entered correctly.

### Modules 8–11 from the PDF
- Module 8 Notification System: basic notification pages exist, but project/task/procurement/attendance/deadline automation needs end-to-end integration.
- Module 9 Dashboard & Analytics: role dashboards and analytics screens exist, but charts should be checked against the required metrics and live data.
- Module 10 Reports & Documentation: reports screen exists; PDF export and Excel export are still required by the specification.
- Module 11 Budget & Cost Management: a dedicated budget/cost module (planning, estimation, expense tracking, monitoring and financial reporting) is not present in the reviewed frontend.

### Milestone / tooling gaps from the PDF
- The PDF lists Angular Material, Bootstrap and Chart.js. They are not currently listed in `package.json`; the UI uses custom CSS instead.
- Automated frontend tests are not complete for the newly added Module 3–7 screens.
- Production deployment/configuration (AWS/Azure/Render), production environment variables and full end-to-end testing remain.

## Recommended local validation
1. Use the Node version required by `.nvmrc` / Angular 22.
2. Delete the copied `node_modules` folder if present.
3. Run `npm ci`.
4. Run `npm run build`.
5. Start FastAPI on `http://localhost:8000` and Angular on `http://localhost:4200`.
6. Test each role separately, especially Admin vs Project Manager vs Site Engineer permissions.
