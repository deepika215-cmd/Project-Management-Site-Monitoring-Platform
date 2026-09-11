# BuildTrack Presentation Demo Data, Notification Icons and Font Update

## Added demo records to the bundled backend database

The included backend/buildtrack.db now contains presentation-ready sample data:

- 5 demo projects:
  - Green Heights Apartments
  - SkyPoint Commercial Complex
  - Chennai Link Road Upgrade
  - Sunrise Medical Block
  - Northside Warehouse
- 4 demo workers:
  - Arun Kumar
  - Meena Priya
  - Karthik Raj
  - Prakash Selvam
- 2 demo contractors:
  - Apex Contracts
  - Metro Builders
- Sample worker assignments and attendance records
- Sample resources and machinery:
  - Tower Crane TC-01
  - Excavator EX-22
  - Concrete Mixer CM-08
  - Dump Truck DT-14
  - Diesel Generator DG-06
  - Safety Helmet Set
- Sample resource allocations
- Sample project milestones
- Sample notifications for project, budget, resource, maintenance, worker attendance and client updates

Current database counts after seeding:
- Projects: 8
- Workers: 7
- Resources: 8
- Machinery: 9
- Resource allocations: 11
- Worker assignments: 5
- Attendance records: 5
- Notifications: 16

## Auto-seed support

Added `_ensure_presentation_demo_data()` in `backend/app/main.py`.

This means the same sample data is also re-created automatically on local SQLite startup if it is missing.

To disable demo data seeding later, set this environment variable in `backend/.env`:

```env
BUILDTRACK_PRESENTATION_DEMO_DATA=0
```

## Notification icon update

Updated all notification pages to show category-aware icons:

- Project/milestone/progress notifications: 📌
- Resource/equipment/machinery notifications: 🏗️
- Worker/attendance/shift notifications: 👷
- Budget/cost/payment/invoice notifications: ₹
- Maintenance/service notifications: 🛠️
- Warning/alert/delay notifications: ⚠️
- General notifications: 🔔

Updated notification pages:
- `frontend/src/app/pages/notifications`
- `frontend/src/app/pages/admin-notifications`
- `frontend/src/app/pages/site-engineer-notifications`
- `frontend/src/app/pages/contractor-notifications`
- `frontend/src/app/pages/worker-notifications`
- `frontend/src/app/pages/client-notifications`

## Font size update

Increased global font size again for better classroom/projector presentation.

Updated:
- `frontend/src/styles.css`

New global scale:
- Base text: 16px
- Small text: 15px
- Table/header compact text: 14px
- Section headings: 23px
- Page headings: 35px

## Validation

- Backend Python compile: Passed
- Frontend TypeScript syntax check: Passed
- ZIP integrity check: Passed
