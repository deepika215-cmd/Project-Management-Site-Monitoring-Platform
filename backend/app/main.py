from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine, SessionLocal


# ============================================================
# IMPORT MODELS
# ============================================================

from app.models.user import User
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.task import Task
from app.models.project_schedule import ProjectScheduleActivity

from app.models.resource import Resource
from app.models.resource_category import ResourceCategory
from app.models.resource_allocation import ResourceAllocation
from app.models.resource_utilization import ResourceUtilization
from app.models.machinery import Machinery
from app.models.maintenance import Maintenance
from app.models.inventory import Inventory
from app.models.document import Document


# ============================================================
# WORKFORCE MANAGEMENT MODELS
# ============================================================

from app.models.worker import Worker
from app.models.contractor import Contractor
from app.models.worker_assignment import WorkerAssignment
from app.models.workforce_category import WorkforceCategory
from app.models.attendance import Attendance
from app.models.shift import Shift
from app.models.payroll import Payroll


# ============================================================
# OTHER MODELS
# ============================================================

from app.models.procurement import Procurement
from app.models.notification import Notification
from app.models.report import Report


# ============================================================
# MODULE 3 — SITE PROGRESS MONITORING MODELS
# ============================================================

from app.models.daily_progress import DailyProgress
from app.models.weekly_progress import WeeklyProgress
from app.models.delay_record import DelayRecord
from app.models.progress_photo import ProgressPhoto
from app.models.site_activity_log import SiteActivityLog


# ============================================================
# MODULE 11 — BUDGET & COST MANAGEMENT MODELS
# ============================================================

from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.models.expense import Expense


# ============================================================
# IMPORT ROUTERS
# ============================================================

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.project import router as project_router
from app.api.milestone import router as milestone_router


# ============================================================
# PROJECT ENGINEER ASSIGNMENT
# ============================================================

from app.api.project_engineer_assignment import (
    router as project_engineer_assignment_router
)


# ============================================================
# TASK MANAGEMENT — MODULE 8
# ============================================================

from app.api.task import router as task_router
from app.api.project_schedule import router as project_schedule_router


# ============================================================
# RESOURCE MANAGEMENT
# ============================================================

from app.api.resource import router as resource_router

from app.api.resource_category import (
    router as resource_category_router
)

from app.api.resource_allocation import (
    router as resource_allocation_router
)

from app.api.resource_utilization import (
    router as resource_utilization_router
)

from app.api.machinery import router as machinery_router
from app.api.maintenance import router as maintenance_router
from app.api.inventory import router as inventory_router


# ============================================================
# WORKFORCE MANAGEMENT ROUTERS
# ============================================================

from app.api.worker import router as worker_router
from app.api.contractor import router as contractor_router
from app.api.worker_assignment import (
    router as worker_assignment_router
)
from app.api.workforce_category import (
    router as workforce_category_router
)
from app.api.attendance import router as attendance_router
from app.api.shift import router as shift_router
from app.api.payroll import router as payroll_router


# ============================================================
# OTHER ROUTERS
# ============================================================

from app.api.procurement import router as procurement_router
from app.api.procurement_request import router as procurement_request_router
from app.api.procurement_request_item import router as procurement_request_item_router
from app.api.vendor import router as vendor_router
from app.api.purchase_order import router as purchase_order_router
from app.api.purchase_order_item import router as purchase_order_item_router
from app.api.invoice import router as invoice_router
from app.api.notification import router as notification_router
from app.api.report import router as report_router


# ============================================================
# ANALYTICS
# ============================================================

from app.api.analytics import router as analytics_router


# ============================================================
# MODULE 3 — SITE PROGRESS MONITORING ROUTERS
# ============================================================

from app.api.daily_progress import router as daily_progress_router
from app.api.weekly_progress import router as weekly_progress_router
from app.api.delay_record import router as delay_record_router
from app.api.progress_photo import router as progress_photo_router
from app.api.site_activity_log import router as site_activity_log_router


# ============================================================
# MATERIAL & INVENTORY MANAGEMENT ROUTERS
# ============================================================

from app.api.material import router as material_router
from app.api.material_request import (
    router as material_request_router
)
from app.api.material_allocation import (
    router as material_allocation_router
)
from app.api.stock_movement import (
    router as stock_movement_router
)


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

from app.api.document import router as document_router


# ============================================================
# MODULE 11 — BUDGET & COST MANAGEMENT ROUTERS
# ============================================================

from app.api.budget import router as budget_router
from app.api.budget_category import router as budget_category_router
from app.api.cost_estimate import router as cost_estimate_router
from app.api.expense import router as expense_router
from app.api.budget_monitoring import router as budget_monitoring_router
from app.api.cost_comparison import router as cost_comparison_router


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)

# ============================================================
# LIGHTWEIGHT SQLITE SCHEMA GUARD FOR MODULE 11
# ============================================================

def ensure_module11_sqlite_schema() -> None:
    """Keep old local SQLite databases compatible with the Module 11 models.

    SQLAlchemy create_all() creates missing tables, but it does not add columns
    to tables that already existed from an older backend. This guard prevents
    Budget & Cost pages from getting stuck on Saving... because of an outdated
    local buildtrack.db schema.
    """
    if not str(engine.url).startswith("sqlite"):
        return
    from sqlalchemy import text
    required_columns = {
        "budgets": [
            ("category_id", "INTEGER"),
            ("allocated_amount", "FLOAT DEFAULT 0"),
            ("description", "VARCHAR(500)"),
            ("status", "VARCHAR(50) DEFAULT 'Active'"),
            ("start_date", "DATE"),
            ("end_date", "DATE"),
        ],
        "cost_estimates": [
            ("budget_id", "INTEGER"),
            ("category_id", "INTEGER"),
            ("item_name", "VARCHAR(200) DEFAULT 'Cost Estimate'"),
            ("quantity", "FLOAT DEFAULT 1"),
            ("unit", "VARCHAR(50)"),
            ("unit_cost", "FLOAT DEFAULT 0"),
            ("estimated_amount", "FLOAT DEFAULT 0"),
            ("description", "VARCHAR(500)"),
            ("estimate_date", "DATE"),
        ],
        "expenses": [
            ("budget_id", "INTEGER"),
            ("category_id", "INTEGER"),
            ("expense_name", "VARCHAR(200) DEFAULT 'Project Expense'"),
            ("amount", "FLOAT DEFAULT 0"),
            ("description", "VARCHAR(500)"),
            ("expense_date", "DATE"),
            ("payment_status", "VARCHAR(50) DEFAULT 'Pending'"),
            ("supplier", "VARCHAR(200)"),
            ("reference", "VARCHAR(200)"),
            ("source_module", "VARCHAR(100) DEFAULT 'MANUAL'"),
        ],
    }
    with engine.begin() as conn:
        for table, columns in required_columns.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
            if not existing:
                continue
            for name, ddl in columns:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))

ensure_module11_sqlite_schema()


# ============================================================
# LIGHTWEIGHT SQLITE SCHEMA GUARD FOR CORE USER/NOTIFICATION TABLES
# ============================================================

def ensure_core_sqlite_schema() -> None:
    """Keep old local SQLite databases compatible with profile and notification pages.

    create_all() does not add columns to existing SQLite tables. Missing or NULL
    columns in users/notifications can make /auth/me or /notification/my return
    a 500 error, which previously left the Angular pages stuck on Loading...
    """
    if not str(engine.url).startswith("sqlite"):
        return

    from sqlalchemy import text

    required_columns = {
        "users": [
            ("phone", "VARCHAR(20)"),
            ("employee_id", "VARCHAR(50)"),
            ("department", "VARCHAR(100)"),
            ("address", "VARCHAR(300)"),
            ("is_active", "BOOLEAN DEFAULT 1"),
            ("created_at", "DATETIME"),
        ],
        "notifications": [
            ("title", "VARCHAR(200) DEFAULT 'Notification'"),
            ("message", "VARCHAR(500) DEFAULT ''"),
            ("recipient", "VARCHAR(100) DEFAULT 'ALL'"),
            ("status", "VARCHAR(50) DEFAULT 'Unread'"),
            ("created_at", "DATETIME"),
        ],
    }

    with engine.begin() as conn:
        for table, columns in required_columns.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
            if not existing:
                continue
            for name, ddl in columns:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))

        conn.execute(text("UPDATE users SET phone = '0000000000' WHERE phone IS NULL OR phone = ''"))
        conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
        conn.execute(text("UPDATE notifications SET title = 'Notification' WHERE title IS NULL OR title = ''"))
        conn.execute(text("UPDATE notifications SET message = '' WHERE message IS NULL"))
        conn.execute(text("UPDATE notifications SET recipient = 'ALL' WHERE recipient IS NULL OR recipient = ''"))
        conn.execute(text("UPDATE notifications SET status = 'Unread' WHERE status IS NULL OR status = ''"))

ensure_core_sqlite_schema()



def _ensure_budget_categories() -> None:
    """Seed the six Module 11 cost categories in local/production databases."""
    categories = [
        ("Labor Cost", "Workforce and labor expenditure"),
        ("Material Cost", "Construction materials and inventory"),
        ("Equipment Cost", "Equipment and machinery expenditure"),
        ("Transportation Cost", "Transport and logistics expenditure"),
        ("Maintenance Cost", "Maintenance and servicing expenditure"),
        ("Administrative Cost", "Administrative and miscellaneous expenditure"),
    ]
    db = SessionLocal()
    try:
        for name, description in categories:
            if not db.query(BudgetCategory).filter(BudgetCategory.name == name).first():
                db.add(BudgetCategory(name=name, description=description))
        db.commit()
    finally:
        db.close()


_ensure_budget_categories()


def _ensure_workforce_defaults() -> None:
    """Seed records required by Workforce screens so create/save forms do not fail on a fresh DB."""
    categories = [
        ("Skilled Worker", "General skilled construction workforce"),
        ("Unskilled Worker", "General helper workforce"),
        ("Engineer", "Engineering workforce"),
        ("Supervisor", "Site supervision workforce"),
        ("Mason", "Masonry workforce"),
        ("Electrician", "Electrical workforce"),
        ("Plumber", "Plumbing workforce"),
        ("Carpenter", "Carpentry workforce"),
        ("Consultant", "External consultant workforce"),
    ]
    db = SessionLocal()
    try:
        for name, description in categories:
            row = db.query(WorkforceCategory).filter(WorkforceCategory.name == name).first()
            if row is None:
                db.add(WorkforceCategory(name=name, description=description, status="Active"))
            else:
                row.status = row.status or "Active"
        if not db.query(Contractor).first():
            db.add(Contractor(name="Default Contractor", company_name="BuildTrack", phone="0000000000", email="contractor@buildtrack.com", status="Active"))
        db.commit()
    finally:
        db.close()


_ensure_workforce_defaults()


def _normalize_legacy_roles() -> None:
    """Migrate old MANAGER/ENGINEER values to canonical frontend roles."""
    db = SessionLocal()
    try:
        changed = False
        for user in db.query(User).all():
            role = str(user.role or "").strip().upper()
            if role == "MANAGER":
                user.role = "PROJECT_MANAGER"
                changed = True
            elif role == "ENGINEER":
                user.role = "SITE_ENGINEER"
                changed = True
        if changed:
            db.commit()
    finally:
        db.close()


_normalize_legacy_roles()


def _ensure_local_demo_accounts() -> None:
    """Ensure predictable local demo accounts exist for project testing.

    Enabled only for SQLite/local development. Set BUILDTRACK_DEMO_ACCOUNTS=0
    to disable it. Existing demo-account passwords are refreshed so the
    documented credentials always work after database copies/resets.
    """
    import os
    from app.database.database import DATABASE_URL
    from app.core.security import hash_password

    if not DATABASE_URL.startswith("sqlite"):
        return
    if os.getenv("BUILDTRACK_DEMO_ACCOUNTS", "1").strip().lower() in {"0", "false", "no"}:
        return

    demo_accounts = [
        ("BuildTrack Admin", "admin@buildtrack.com", "Admin@123", "ADMIN"),
        ("Project Manager", "manager@buildtrack.com", "Manager@123", "PROJECT_MANAGER"),
        ("Site Engineer", "engineer@buildtrack.com", "Engineer@123", "SITE_ENGINEER"),
        ("Contractor", "contractor@buildtrack.com", "Contractor@123", "CONTRACTOR"),
        ("Worker", "worker@buildtrack.com", "Worker@123", "WORKER"),
        ("Client", "client@buildtrack.com", "Client@123", "CLIENT"),
    ]

    db = SessionLocal()
    try:
        for name, email, password, role in demo_accounts:
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                user = User(name=name, email=email, phone="0000000000", role=role, is_active=True)
                db.add(user)
            user.name = name
            user.role = role
            if hasattr(user, "employee_id") and not user.employee_id:
                user.employee_id = role.replace("_", "-") + "-DEMO"
            if hasattr(user, "department") and not user.department:
                user.department = "BuildTrack"
            user.is_active = True
            if not user.phone:
                user.phone = "0000000000"
            user.password = hash_password(password)
        db.commit()
    finally:
        db.close()


_ensure_local_demo_accounts()


def _ensure_presentation_demo_data() -> None:
    """Seed presentation-ready demo data for local SQLite runs.

    This gives the project enough realistic records to demonstrate dashboards,
    projects, workforce, resources and notifications immediately after starting
    the backend. Disable with BUILDTRACK_PRESENTATION_DEMO_DATA=0.
    """
    import os
    from datetime import date, datetime

    from app.database.database import DATABASE_URL

    if not DATABASE_URL.startswith("sqlite"):
        return
    if os.getenv("BUILDTRACK_PRESENTATION_DEMO_DATA", "1").strip().lower() in {"0", "false", "no"}:
        return

    db = SessionLocal()
    try:
        manager = db.query(User).filter(User.email == "manager@buildtrack.com").first()
        engineer = db.query(User).filter(User.email == "engineer@buildtrack.com").first()
        manager_id = manager.id if manager else None
        engineer_id = engineer.id if engineer else None

        def get_or_create_project(code, name, category, priority, description, location, start, end, budget, status):
            project = db.query(Project).filter(Project.project_code == code).first()
            if project is None:
                project = Project(project_code=code)
                db.add(project)
            project.project_name = name
            project.project_category = category
            project.priority = priority
            project.description = description
            project.location = location
            project.start_date = date.fromisoformat(start)
            project.end_date = date.fromisoformat(end)
            project.budget = budget
            project.status = status
            project.manager_id = manager_id
            project.inspection_approved = False
            project.financial_settlement_complete = False
            project.pending_issues_resolved = False
            project.client_accepted = False
            db.flush()
            if engineer_id and not db.query(ProjectEngineerAssignment).filter_by(project_id=project.id, engineer_id=engineer_id).first():
                db.add(ProjectEngineerAssignment(project_id=project.id, engineer_id=engineer_id))
            return project

        projects = {
            "DEMO-PROJ-001": get_or_create_project(
                "DEMO-PROJ-001", "Green Heights Apartments", "Residential", "High",
                "12-floor residential apartment construction with parking and rooftop solar.",
                "Chennai, Tamil Nadu", "2026-09-01", "2027-03-31", 8500000, "In Progress"
            ),
            "DEMO-PROJ-002": get_or_create_project(
                "DEMO-PROJ-002", "SkyPoint Commercial Complex", "Commercial", "Critical",
                "Commercial office complex with retail frontage and basement parking.",
                "Guindy, Chennai", "2026-08-20", "2027-05-15", 14200000, "In Progress"
            ),
            "DEMO-PROJ-003": get_or_create_project(
                "DEMO-PROJ-003", "Chennai Link Road Upgrade", "Infrastructure", "Medium",
                "Road widening, storm-water drain and pavement strengthening works.",
                "Tambaram, Chennai", "2026-10-05", "2027-02-20", 6200000, "Planning"
            ),
            "DEMO-PROJ-004": get_or_create_project(
                "DEMO-PROJ-004", "Sunrise Medical Block", "Healthcare", "High",
                "New hospital wing with electrical, plumbing and HVAC packages.",
                "Velachery, Chennai", "2026-07-15", "2027-01-30", 9800000, "In Progress"
            ),
            "DEMO-PROJ-005": get_or_create_project(
                "DEMO-PROJ-005", "Northside Warehouse", "Industrial", "Medium",
                "Pre-engineered warehouse construction with loading bays and safety systems.",
                "Red Hills, Chennai", "2026-09-20", "2027-04-05", 7300000, "On Hold"
            ),
        }

        for name, description in [
            ("Cranes", "Tower and mobile cranes"),
            ("Excavators", "Excavation machinery"),
            ("Concrete Equipment", "Concrete mixer and pump equipment"),
            ("Transport", "Dump trucks and material movement vehicles"),
            ("Power", "Generators and electrical support equipment"),
            ("Safety", "Safety gear and site protection resources"),
        ]:
            category = db.query(ResourceCategory).filter(ResourceCategory.name == name).first()
            if category is None:
                db.add(ResourceCategory(name=name, description=description, status="Active"))

        def get_or_create_contractor(email, name, company, phone):
            contractor = db.query(Contractor).filter(Contractor.email == email).first()
            if contractor is None:
                contractor = Contractor(email=email)
                db.add(contractor)
            contractor.name = name
            contractor.company_name = company
            contractor.phone = phone
            contractor.status = "Active"
            db.flush()
            return contractor

        contractor1 = get_or_create_contractor("apex.contracts@buildtrack.demo", "Apex Contracts", "Apex Civil Works", "9000011111")
        contractor2 = get_or_create_contractor("metro.builders@buildtrack.demo", "Metro Builders", "Metro Build Associates", "9000022222")

        def get_or_create_worker(email, name, phone, skill, contractor):
            worker = db.query(Worker).filter(Worker.email == email).first()
            if worker is None:
                worker = Worker(email=email)
                db.add(worker)
            worker.name = name
            worker.role = "Worker"
            worker.phone = phone
            worker.category = "Skilled Worker"
            worker.skill_type = skill
            worker.contractor_id = contractor.id
            worker.joining_date = "2026-08-01"
            worker.status = "Active"
            db.flush()
            return worker

        workers = [
            get_or_create_worker("arun.worker@buildtrack.demo", "Arun Kumar", "9100010001", "Masonry", contractor1),
            get_or_create_worker("meena.electrician@buildtrack.demo", "Meena Priya", "9100010002", "Electrical", contractor1),
            get_or_create_worker("karthik.plumber@buildtrack.demo", "Karthik Raj", "9100010003", "Plumbing", contractor2),
            get_or_create_worker("prakash.carpenter@buildtrack.demo", "Prakash Selvam", "9100010004", "Carpentry", contractor2),
        ]

        assignments = [
            (workers[0], contractor1, projects["DEMO-PROJ-001"], "Block A masonry work", "2026-09-06", "2026-10-15", "ACTIVE"),
            (workers[1], contractor1, projects["DEMO-PROJ-004"], "Electrical conduit installation", "2026-09-08", "2026-10-05", "ACTIVE"),
            (workers[2], contractor2, projects["DEMO-PROJ-002"], "Plumbing line installation", "2026-09-10", "2026-10-20", "ACTIVE"),
            (workers[3], contractor2, projects["DEMO-PROJ-005"], "Warehouse shutter and carpentry", "2026-09-12", "2026-11-01", "PLANNED"),
        ]
        for worker, contractor, project, activity, start, end, status in assignments:
            if not db.query(WorkerAssignment).filter_by(worker_id=worker.id, project_id=project.id, work_activity=activity).first():
                db.add(WorkerAssignment(
                    worker_id=worker.id, contractor_id=contractor.id, project_id=project.id,
                    work_activity=activity, assignment_start_date=start, assignment_end_date=end,
                    assignment_status=status
                ))

        today = date.today().isoformat()
        attendance = [
            (workers[0], projects["DEMO-PROJ-001"], "Present", "08:30", "17:00", 8.5, "Demo attendance for presentation"),
            (workers[1], projects["DEMO-PROJ-004"], "Present", "08:45", "17:15", 8.5, "Electrical work in progress"),
            (workers[2], projects["DEMO-PROJ-002"], "Present", "09:00", "17:00", 8.0, "Plumbing work in progress"),
            (workers[3], projects["DEMO-PROJ-005"], "Absent", None, None, 0.0, "Planned shift not started"),
        ]
        for worker, project, status, check_in, check_out, hours, remarks in attendance:
            if not db.query(Attendance).filter_by(worker_id=worker.id, date=today).first():
                db.add(Attendance(
                    worker_id=worker.id, project_id=project.id, date=today, status=status,
                    check_in_time=check_in, check_out_time=check_out, working_hours=hours,
                    remarks=remarks, used=0
                ))

        def get_or_create_resource(name, resource_type, quantity, allocated, status, project):
            resource = db.query(Resource).filter(Resource.name == name).first()
            if resource is None:
                resource = Resource(name=name)
                db.add(resource)
            resource.type = resource_type
            resource.quantity = quantity
            resource.allocated_quantity = allocated
            resource.status = status
            resource.project_id = project.id
            db.flush()
            return resource

        resources = [
            get_or_create_resource("Tower Crane TC-01", "Cranes", 2, 1, "Allocated", projects["DEMO-PROJ-002"]),
            get_or_create_resource("Excavator EX-22", "Excavators", 3, 2, "Allocated", projects["DEMO-PROJ-003"]),
            get_or_create_resource("Concrete Mixer CM-08", "Concrete Equipment", 5, 2, "Available", projects["DEMO-PROJ-001"]),
            get_or_create_resource("Dump Truck DT-14", "Transport", 4, 1, "Available", projects["DEMO-PROJ-003"]),
            get_or_create_resource("Diesel Generator DG-06", "Power", 6, 2, "Allocated", projects["DEMO-PROJ-004"]),
            get_or_create_resource("Safety Helmet Set", "Safety", 120, 65, "Available", projects["DEMO-PROJ-001"]),
        ]

        for resource, project, worker, quantity, person in [
            (resources[0], projects["DEMO-PROJ-002"], workers[2], 1, "Karthik Raj"),
            (resources[1], projects["DEMO-PROJ-003"], workers[0], 2, "Arun Kumar"),
            (resources[4], projects["DEMO-PROJ-004"], workers[1], 2, "Meena Priya"),
            (resources[5], projects["DEMO-PROJ-001"], workers[0], 65, "Arun Kumar"),
        ]:
            if not db.query(ResourceAllocation).filter_by(resource_id=resource.id, project_id=project.id, worker_id=worker.id).first():
                db.add(ResourceAllocation(
                    resource_id=resource.id, project_id=project.id, worker_id=worker.id,
                    quantity=quantity, allocation_date=date.today(), expected_return_date=date(2026, 10, 15),
                    responsible_person=person, status="Allocated"
                ))

        machinery_rows = [
            ("EQ-DEMO-001", "Tower Crane TC-01", "Crane", "SkyPoint Site", "Operating", "Ramesh", 128.5, projects["DEMO-PROJ-002"]),
            ("EQ-DEMO-002", "Excavator EX-22", "Excavator", "Road Upgrade Zone A", "Operating", "Vijay", 96.0, projects["DEMO-PROJ-003"]),
            ("EQ-DEMO-003", "Concrete Mixer CM-08", "Concrete Mixer", "Green Heights Block A", "Available", "Murugan", 74.0, projects["DEMO-PROJ-001"]),
            ("EQ-DEMO-004", "Dump Truck DT-14", "Dump Truck", "Road Upgrade Depot", "Available", "Sathish", 52.5, projects["DEMO-PROJ-003"]),
            ("EQ-DEMO-005", "Diesel Generator DG-06", "Generator", "Sunrise Medical Block", "Maintenance", "Service Team", 210.0, projects["DEMO-PROJ-004"]),
        ]
        for equipment_id, name, machinery_type, location, status, operator, hours_used, project in machinery_rows:
            machine = db.query(Machinery).filter(Machinery.equipment_id == equipment_id).first()
            if machine is None:
                machine = Machinery(equipment_id=equipment_id)
                db.add(machine)
            machine.name = name
            machine.machinery_type = machinery_type
            machine.location = location
            machine.status = status
            machine.operator = operator
            machine.hours_used = hours_used
            machine.project_id = project.id

        milestones = [
            (projects["DEMO-PROJ-001"], "Foundation Completed", "Foundation and footing work completed", "2026-09-25", "In Progress"),
            (projects["DEMO-PROJ-002"], "Basement Excavation", "Basement excavation and shoring", "2026-09-30", "In Progress"),
            (projects["DEMO-PROJ-004"], "MEP Rough-In", "Mechanical, electrical and plumbing rough-in", "2026-10-10", "Pending"),
        ]
        for project, title, description, due_date, status in milestones:
            if not db.query(ProjectMilestone).filter_by(project_id=project.id, title=title).first():
                db.add(ProjectMilestone(
                    project_id=project.id, title=title, description=description,
                    due_date=date.fromisoformat(due_date), status=status
                ))

        notifications = [
            ("Project Update", "Green Heights Apartments reached foundation milestone target.", "ALL", "Unread"),
            ("Resource Alert", "Tower Crane TC-01 is allocated to SkyPoint Commercial Complex.", "PROJECT_MANAGER", "Unread"),
            ("Worker Attendance", "Three workers marked present for today's site shift.", "CONTRACTOR", "Unread"),
            ("Budget Warning", "SkyPoint Commercial Complex utilization is nearing the planned monthly budget limit.", "ADMIN", "Unread"),
            ("Maintenance Due", "Diesel Generator DG-06 is scheduled for preventive maintenance.", "SITE_ENGINEER", "Unread"),
            ("Client Update", "Sunrise Medical Block weekly progress summary is ready for review.", "CLIENT", "Unread"),
        ]
        for title, message, recipient, status in notifications:
            if not db.query(Notification).filter_by(title=title, message=message).first():
                db.add(Notification(
                    title=title, message=message, recipient=recipient,
                    status=status, created_at=datetime.utcnow()
                ))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


_ensure_presentation_demo_data()




# ============================================================
# PRESENTATION PAGE DEMO DATA FOR SELECTED SCREENSHOTS
# ============================================================

def _ensure_presentation_page_records() -> None:
    """Seed the pages used in the final presentation screenshots.

    This keeps the Worker Dashboard, Budget & Cost, Procurement, Material
    Inventory and Project Scheduling pages from looking empty after a fresh
    local database reset. Disable with BUILDTRACK_PRESENTATION_DEMO_DATA=0.
    """
    import os
    from datetime import date, datetime, timedelta
    from sqlalchemy import text
    from app.database.database import DATABASE_URL

    if not DATABASE_URL.startswith("sqlite"):
        return
    if os.getenv("BUILDTRACK_PRESENTATION_DEMO_DATA", "1").strip().lower() in {"0", "false", "no"}:
        return

    today = date.today()

    def table_cols(conn, table):
        return {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}

    def insert_filtered(conn, table, data):
        cols = table_cols(conn, table)
        data = {k: v for k, v in data.items() if k in cols}
        if not data:
            return None
        names = list(data.keys())
        sql = f"INSERT INTO {table} ({','.join(names)}) VALUES ({','.join(':'+n for n in names)})"
        result = conn.execute(text(sql), data)
        return result.lastrowid

    def scalar(conn, sql, params=None):
        row = conn.execute(text(sql), params or {}).fetchone()
        return row[0] if row else None

    def upsert_by(conn, table, key_col, key_val, data):
        row_id = scalar(conn, f"SELECT id FROM {table} WHERE {key_col}=:v", {"v": key_val})
        cols = table_cols(conn, table)
        data = {k: v for k, v in data.items() if k in cols}
        if row_id:
            set_cols = [k for k in data if k != "id"]
            if set_cols:
                params = {k: data[k] for k in set_cols}
                params["id"] = row_id
                conn.execute(text(f"UPDATE {table} SET {','.join(c+'=:'+c for c in set_cols)} WHERE id=:id"), params)
            return row_id
        return insert_filtered(conn, table, data)

    with engine.begin() as conn:
        admin_id = scalar(conn, "SELECT id FROM users WHERE email='admin@buildtrack.com'") or 1
        manager_id = scalar(conn, "SELECT id FROM users WHERE email='manager@buildtrack.com'") or admin_id
        engineer_id = scalar(conn, "SELECT id FROM users WHERE email='engineer@buildtrack.com'") or manager_id

        project_id = scalar(conn, "SELECT id FROM projects WHERE project_name='BuildTrack Test Project'")
        if not project_id:
            project_id = insert_filtered(conn, "projects", {
                "project_name":"BuildTrack Test Project", "project_code":"BT-TEST-001", "project_category":"Commercial",
                "priority":"High", "description":"Demo construction project with sample presentation data.",
                "location":"Hyderabad", "start_date":"2026-09-05", "end_date":"2027-09-05",
                "budget":5000000, "status":"In Progress", "manager_id":manager_id,
                "inspection_approved":0, "financial_settlement_complete":0, "pending_issues_resolved":0, "client_accepted":0,
            })
        else:
            conn.execute(text("""
                UPDATE projects SET status='In Progress', budget=5000000,
                description='Demo construction project with sample presentation data.', manager_id=:manager_id
                WHERE id=:project_id
            """), {"manager_id": manager_id, "project_id": project_id})

        if engineer_id and not scalar(conn, "SELECT id FROM project_engineer_assignments WHERE project_id=:p AND engineer_id=:e", {"p":project_id,"e":engineer_id}):
            insert_filtered(conn, "project_engineer_assignments", {"project_id":project_id,"engineer_id":engineer_id,"assigned_at":datetime.utcnow()})

        contractor_id = upsert_by(conn, "contractors", "email", "contractor@buildtrack.com", {
            "name":"BuildTrack Demo Contractor", "company_name":"Apex Civil Works", "phone":"9000011111",
            "email":"contractor@buildtrack.com", "status":"Active"
        })
        worker_id = upsert_by(conn, "workers", "email", "worker@buildtrack.com", {
            "name":"Ravi Kumar", "role":"Worker", "phone":"9876543210", "email":"worker@buildtrack.com",
            "category":"Skilled Worker", "skill_type":"Masonry", "contractor_id":contractor_id,
            "joining_date":"2026-08-01", "status":"Active"
        })
        for demo_email, name, phone, skill in [
            ("suresh.worker@buildtrack.demo","Suresh Kumar","9876543211","Carpentry"),
            ("meena.electrician@buildtrack.demo","Meena Priya","9876543212","Electrical"),
            ("karthik.plumber@buildtrack.demo","Karthik Raj","9876543213","Plumbing"),
        ]:
            upsert_by(conn, "workers", "email", demo_email, {
                "name":name,"role":"Worker","phone":phone,"email":demo_email,"category":"Skilled Worker",
                "skill_type":skill,"contractor_id":contractor_id,"joining_date":"2026-08-05","status":"Active"
            })
        if not scalar(conn, "SELECT id FROM worker_assignments WHERE worker_id=:w AND project_id=:p", {"w":worker_id,"p":project_id}):
            insert_filtered(conn, "worker_assignments", {
                "worker_id":worker_id,"contractor_id":contractor_id,"project_id":project_id,
                "work_activity":"Block A masonry and brick work","assignment_start_date":"2026-09-06",
                "assignment_end_date":"2026-10-15","assignment_status":"ACTIVE"
            })
        for offset, status, cin, cout, hours, remarks in [
            (0,"Present","08:30","17:00",8.5,"Masonry work completed"),
            (1,"Present","08:45","17:10",8.4,"Foundation block work"),
            (2,"Absent",None,None,0.0,"Leave"),
            (3,"Present","08:40","17:00",8.3,"Site preparation"),
        ]:
            d = (today - timedelta(days=offset)).isoformat()
            if not scalar(conn, "SELECT id FROM attendance WHERE worker_id=:w AND date=:d", {"w":worker_id,"d":d}):
                insert_filtered(conn, "attendance", {"worker_id":worker_id,"project_id":project_id,"date":d,"status":status,"check_in_time":cin,"check_out_time":cout,"working_hours":hours,"remarks":remarks,"used":0})

        category_amounts = {
            "Labor Cost": 1200000, "Material Cost": 1850000, "Equipment Cost": 750000,
            "Transportation Cost": 250000, "Maintenance Cost": 180000, "Administrative Cost": 220000,
        }
        for name in category_amounts:
            upsert_by(conn, "budget_categories", "name", name, {"name":name,"description":f"{name} for construction project"})
        conn.execute(text("DELETE FROM budgets WHERE project_id=:p"), {"p":project_id})
        for name, amount in category_amounts.items():
            category_id = scalar(conn, "SELECT id FROM budget_categories WHERE name=:n", {"n":name})
            insert_filtered(conn, "budgets", {"project_id":project_id,"category_id":category_id,"allocated_amount":amount,"description":"Presentation demo budget allocation","status":"Active","start_date":"2026-09-05","end_date":"2027-09-05"})
        conn.execute(text("DELETE FROM cost_estimates WHERE project_id=:p"), {"p":project_id})
        conn.execute(text("DELETE FROM expenses WHERE project_id=:p"), {"p":project_id})
        for item_name, category_name, quantity, unit, unit_cost, description in [
            ("Masonry labour package","Labor Cost",120,"days",2500,"Labor estimate for masonry work"),
            ("OPC cement and TMT steel procurement","Material Cost",1,"package",780000,"Material estimate for foundation and RCC"),
            ("Crane and concrete mixer rental","Equipment Cost",30,"days",12000,"Equipment rental estimate"),
        ]:
            category_id = scalar(conn, "SELECT id FROM budget_categories WHERE name=:n", {"n":category_name})
            insert_filtered(conn, "cost_estimates", {"project_id":project_id,"category_id":category_id,"item_name":item_name,"quantity":quantity,"unit":unit,"unit_cost":unit_cost,"estimated_amount":quantity*unit_cost,"description":description,"estimate_date":today.isoformat()})
        for expense_name, amount, category_name, supplier, reference in [
            ("Initial cement payment",285000,"Material Cost","Dharan Building Supplies","INV-DEMO-001"),
            ("Worker advance payment",140000,"Labor Cost","Apex Civil Works","PAY-DEMO-001"),
            ("Equipment mobilization",90000,"Equipment Cost","Apex Equipment Rentals","EQ-MOB-001"),
        ]:
            category_id = scalar(conn, "SELECT id FROM budget_categories WHERE name=:n", {"n":category_name})
            insert_filtered(conn, "expenses", {"project_id":project_id,"category_id":category_id,"expense_name":expense_name,"amount":amount,"description":expense_name,"expense_date":today.isoformat(),"payment_status":"Paid","supplier":supplier,"reference":reference,"source_module":"PRESENTATION_DEMO"})

        material_data = [("OPC 53 Cement","Cement","bags",100,650),("TMT Steel Bars","Steel","kg",500,3200),("Red Bricks","Bricks","nos",1000,8000),("River Sand","Sand","tons",20,85)]
        material_ids = {}
        for name, category, unit, minimum, qty in material_data:
            material_id = upsert_by(conn, "materials", "name", name, {"name":name,"category":category,"unit":unit,"minimum_stock":minimum})
            material_ids[name] = material_id
            inv_id = scalar(conn, "SELECT id FROM inventory WHERE item_name=:n AND project_id IS NULL", {"n":name})
            if inv_id:
                conn.execute(text("UPDATE inventory SET category=:c, quantity=:q, unit=:u, supplier='Dharan Building Supplies' WHERE id=:id"), {"c":category,"q":qty,"u":unit,"id":inv_id})
            else:
                insert_filtered(conn, "inventory", {"item_name":name,"category":category,"quantity":qty,"unit":unit,"supplier":"Dharan Building Supplies","project_id":None,"resource_id":None})
            conn.execute(text("DELETE FROM stock_movements WHERE material_id=:m"), {"m": material_id})
            insert_filtered(conn, "stock_movements", {"material_id":material_id,"project_id":None,"movement_type":"RECEIVED","quantity":qty,"created_at":datetime.utcnow(),"remarks":"Initial demo stock received"})
        conn.execute(text("DELETE FROM material_requests WHERE project_id=:p"), {"p":project_id})
        conn.execute(text("DELETE FROM material_allocations WHERE project_id=:p"), {"p":project_id})
        for material_name, qty, purpose, status in [("OPC 53 Cement",150,"Foundation concrete work","Approved"),("TMT Steel Bars",800,"RCC column reinforcement","Pending"),("Red Bricks",2000,"Block A wall construction","Approved")]:
            insert_filtered(conn, "material_requests", {"project_id":project_id,"material_id":material_ids[material_name],"quantity":qty,"required_date":(today+timedelta(days=7)).isoformat(),"purpose":purpose,"remarks":"Presentation demo request","status":status})
        insert_filtered(conn, "material_allocations", {"project_id":project_id,"material_id":material_ids["OPC 53 Cement"],"quantity":100,"allocation_date":today.isoformat(),"work_activity":"Foundation concrete work","responsible_user":"Ravi Kumar","status":"ALLOCATED"})
        insert_filtered(conn, "stock_movements", {"material_id":material_ids["OPC 53 Cement"],"project_id":project_id,"movement_type":"ALLOCATED","quantity":100,"created_at":datetime.utcnow(),"remarks":"Allocated to foundation concrete work"})
        insert_filtered(conn, "material_allocations", {"project_id":project_id,"material_id":material_ids["Red Bricks"],"quantity":500,"allocation_date":today.isoformat(),"work_activity":"Block A wall construction","responsible_user":"Ravi Kumar","status":"CONSUMED"})
        insert_filtered(conn, "stock_movements", {"material_id":material_ids["Red Bricks"],"project_id":project_id,"movement_type":"ALLOCATED","quantity":500,"created_at":datetime.utcnow(),"remarks":"Allocated to Block A wall construction"})
        insert_filtered(conn, "stock_movements", {"material_id":material_ids["Red Bricks"],"project_id":project_id,"movement_type":"CONSUMED","quantity":500,"created_at":datetime.utcnow(),"remarks":"Consumed in Block A wall construction"})
        conn.execute(text("UPDATE inventory SET quantity=quantity-100 WHERE item_name='OPC 53 Cement' AND project_id IS NULL"))
        conn.execute(text("UPDATE inventory SET quantity=quantity-500 WHERE item_name='Red Bricks' AND project_id IS NULL"))

        vendor_ids = {}
        for vendor_name, person, phone, email, category, service in [
            ("Dharan Building Supplies","Dharan","9150164664","dharan.supplies@example.com","Raw Materials","Cement, sand and bricks"),
            ("Sri Lakshmi Steel Traders","Lakshmi","9150164665","steel.traders@example.com","Raw Materials","TMT steel bars"),
            ("Apex Equipment Rentals","Arun","9150164666","apex.equipment@example.com","Machinery","Crane and excavator rental"),
        ]:
            vendor_ids[vendor_name] = upsert_by(conn, "vendors", "vendor_name", vendor_name, {"vendor_name":vendor_name,"contact_person":person,"contact_number":phone,"email":email,"address":"Chennai Demo Supplier Yard","category":category,"products_services":service,"status":"ACTIVE"})
        conn.execute(text("DELETE FROM invoices WHERE project_id=:p"), {"p":project_id})
        conn.execute(text("DELETE FROM purchase_orders WHERE project_id=:p"), {"p":project_id})
        conn.execute(text("DELETE FROM procurement_requests WHERE project_id=:p"), {"p":project_id})
        req_id = insert_filtered(conn, "procurement_requests", {"project_id":project_id,"requested_by":manager_id,"item_name":"OPC 53 Cement","category":"Raw Materials","quantity":500,"required_date":(today+timedelta(days=5)).isoformat(),"purpose":"Foundation concrete work","priority":"HIGH","request_date":today.isoformat(),"status":"Approved","remarks":"Demo request approved for presentation"})
        insert_filtered(conn, "procurement_request_items", {"procurement_request_id":req_id,"item_name":"OPC 53 Cement","category":"Raw Materials","quantity":500,"estimated_unit_price":420,"estimated_total_price":210000,"remarks":"Cement bags for foundation"})
        po_id = insert_filtered(conn, "purchase_orders", {"vendor_id":vendor_ids["Dharan Building Supplies"],"project_id":project_id,"procurement_request_id":req_id,"order_date":today.isoformat(),"expected_delivery_date":(today+timedelta(days=4)).isoformat(),"total_amount":210000,"tax_amount":37800,"additional_charges":5000,"overall_amount":252800,"status":"Issued"})
        insert_filtered(conn, "purchase_order_items", {"purchase_order_id":po_id,"item_name":"OPC 53 Cement","category":"Raw Materials","quantity":500,"unit_price":420,"total_price":210000})
        insert_filtered(conn, "invoices", {"invoice_number":"INV-DEMO-001","vendor_id":vendor_ids["Dharan Building Supplies"],"purchase_order_id":po_id,"project_id":project_id,"invoice_date":today.isoformat(),"due_date":(today+timedelta(days=10)).isoformat(),"invoice_amount":252800,"payment_status":"Pending","invoice_status":"Received","remarks":"Demo invoice for material procurement"})
        insert_filtered(conn, "procurement_requests", {"project_id":project_id,"requested_by":engineer_id,"item_name":"TMT Steel Bars","category":"Raw Materials","quantity":800,"required_date":(today+timedelta(days=12)).isoformat(),"purpose":"RCC column reinforcement","priority":"NORMAL","request_date":today.isoformat(),"status":"Pending","remarks":"Waiting for manager approval"})

        for name, typ, quantity, allocated, status in [("Tower Crane TC-01","Cranes",2,1,"Allocated"),("Excavator EX-22","Excavators",3,2,"Allocated"),("Concrete Mixer CM-08","Concrete Equipment",5,2,"Available"),("Safety Helmet Set","Safety",120,65,"Available")]:
            upsert_by(conn, "resources", "name", name, {"name":name,"type":typ,"quantity":quantity,"allocated_quantity":allocated,"status":status,"project_id":project_id})
        for equipment_id, name, machinery_type, location, status, operator, hours_used in [("EQ-DEMO-001","Tower Crane TC-01","Crane","BuildTrack Test Project - North Block","Operating","Ramesh",128.5),("EQ-DEMO-002","Excavator EX-22","Excavator","BuildTrack Test Project - Excavation Area","Operating","Vijay",96.0),("EQ-DEMO-003","Concrete Mixer CM-08","Concrete Mixer","BuildTrack Test Project - Block A","Available","Murugan",74.0)]:
            upsert_by(conn, "machinery", "equipment_id", equipment_id, {"equipment_id":equipment_id,"name":name,"machinery_type":machinery_type,"location":location,"status":status,"operator":operator,"hours_used":hours_used,"project_id":project_id})

        conn.execute(text("DELETE FROM project_schedule_activities WHERE project_id=:p"), {"p":project_id})
        schedule_rows = [("Site Preparation","Clearing, marking and safety barricading","2026-09-06","2026-09-10","","Completed"),("Foundation Excavation","Excavation for footings and foundation","2026-09-11","2026-09-18","Site Preparation","In Progress"),("Footing Concrete","PCC, steel placement and footing concrete","2026-09-19","2026-09-26","Foundation Excavation","Not Started"),("RCC Column Casting","Column reinforcement and concrete casting","2026-09-27","2026-10-10","Footing Concrete","Not Started"),("Brickwork Block A","Masonry work for Block A ground floor","2026-10-11","2026-10-28","RCC Column Casting","Not Started")]
        for activity_name, description, start_date, end_date, dependency, status in schedule_rows:
            insert_filtered(conn, "project_schedule_activities", {"project_id":project_id,"activity_name":activity_name,"description":description,"start_date":start_date,"end_date":end_date,"dependency":dependency,"status":status,"created_by":manager_id})

        for title, message, recipient in [("Project Schedule Updated","Five schedule activities were added for BuildTrack Test Project.","ALL"),("Procurement Request Pending","TMT Steel Bars request is waiting for approval.","PROJECT_MANAGER"),("Inventory Stock Added","Cement, steel, bricks and sand demo stock is available.","SITE_ENGINEER"),("Budget Demo Ready","Budget, estimates and expenses are available for BuildTrack Test Project.","ADMIN"),("Worker Linked","Worker dashboard is linked to Ravi Kumar / worker@buildtrack.com.","WORKER")]:
            if not scalar(conn, "SELECT id FROM notifications WHERE title=:t AND message=:m", {"t":title,"m":message}):
                insert_filtered(conn, "notifications", {"title":title,"message":message,"recipient":recipient,"status":"Unread","created_at":datetime.utcnow()})

_ensure_presentation_page_records()



# ============================================================
# CONSISTENT DASHBOARD PRESENTATION DATA
# ============================================================
def _ensure_consistent_dashboard_demo_data() -> None:
    """Keep all role dashboards aligned for local presentation/demo runs.

    The app has role-scoped dashboards. This seed makes the demo Project Manager,
    Site Engineer, Contractor, Worker and Client screens use the same visible
    project set and the same related budget, procurement, inventory, resource,
    workforce, report and notification records.

    Disable with BUILDTRACK_PRESENTATION_DEMO_DATA=0.
    """
    import os
    import sqlite3
    from datetime import date, datetime, timedelta
    from app.database.database import DATABASE_URL

    if not DATABASE_URL.startswith("sqlite"):
        return
    if os.getenv("BUILDTRACK_PRESENTATION_DEMO_DATA", "1").strip().lower() in {"0", "false", "no"}:
        return

    db_file = DATABASE_URL.replace("sqlite:///", "", 1)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    def table_exists(table: str) -> bool:
        return cur.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone() is not None

    def cols(table: str) -> set[str]:
        if not table_exists(table):
            return set()
        return {row["name"] for row in cur.execute(f"pragma table_info({table})")}

    def scalar(sql: str, params: tuple = ()): 
        row = cur.execute(sql, params).fetchone()
        return None if row is None else list(row)[0]

    def insert_filtered(table: str, data: dict):
        available = cols(table)
        if not available:
            return None
        payload = {k: v for k, v in data.items() if k in available}
        if not payload:
            return None
        keys = list(payload)
        cur.execute(f"insert into {table} ({','.join(keys)}) values ({','.join('?' for _ in keys)})", [payload[k] for k in keys])
        return cur.lastrowid

    def upsert(table: str, key: str, value, data: dict):
        if not table_exists(table):
            return None
        row_id = scalar(f"select id from {table} where {key}=?", (value,))
        payload = {k: v for k, v in data.items() if k in cols(table)}
        if row_id:
            if payload:
                cur.execute(f"update {table} set {','.join(f'{k}=?' for k in payload)} where id=?", list(payload.values()) + [row_id])
            return row_id
        payload = {**{key: value}, **payload}
        return insert_filtered(table, payload)

    manager_id = scalar("select id from users where email='manager@buildtrack.com'") or scalar("select id from users where role='PROJECT_MANAGER' order by id limit 1")
    engineer_id = scalar("select id from users where email='engineer@buildtrack.com'") or scalar("select id from users where role='SITE_ENGINEER' order by id limit 1")
    contractor_user_id = scalar("select id from users where email='contractor@buildtrack.com'")
    worker_user_id = scalar("select id from users where email='worker@buildtrack.com'")
    client_id = scalar("select id from users where email='client@buildtrack.com'")

    for uid, name, role in [
        (manager_id, 'Project Manager', 'PROJECT_MANAGER'),
        (engineer_id, 'Site Engineer', 'SITE_ENGINEER'),
        (contractor_user_id, 'Contractor', 'CONTRACTOR'),
        (worker_user_id, 'Worker', 'WORKER'),
        (client_id, 'Client', 'CLIENT')
    ]:
        if uid:
            cur.execute("update users set name=?, role=?, is_active=1 where id=?", (name, role, uid))

    projects = [
        ('BT-TEST-001','BuildTrack Test Project','Commercial','High','Main presentation project with budget, procurement, inventory, workforce, resources and schedule data.','Hyderabad','2026-09-05','2027-09-05',5000000,'In Progress',37),
        ('DEMO-PROJ-001','Green Heights Apartments','Residential','High','12-floor apartment construction with parking and rooftop solar.','Chennai, Tamil Nadu','2026-09-01','2027-03-31',8500000,'In Progress',42),
        ('DEMO-PROJ-002','SkyPoint Commercial Complex','Commercial','Critical','Office complex with retail frontage and basement parking.','Guindy, Chennai','2026-08-20','2027-05-15',14200000,'In Progress',28),
        ('DEMO-PROJ-003','Chennai Link Road Upgrade','Infrastructure','Medium','Road widening, storm-water drain and pavement strengthening.','Tambaram, Chennai','2026-10-05','2027-02-20',6200000,'Planning',8),
        ('DEMO-PROJ-004','Sunrise Medical Block','Healthcare','High','Hospital wing with electrical, plumbing and HVAC packages.','Velachery, Chennai','2026-07-15','2027-01-30',9800000,'In Progress',58),
        ('DEMO-PROJ-005','Northside Warehouse','Industrial','Medium','Pre-engineered warehouse with loading bays and safety systems.','Red Hills, Chennai','2026-09-20','2027-04-05',7300000,'On Hold',19),
    ]
    project_ids = []
    for code, name, cat, priority, desc, location, start, end, budget, status, progress in projects:
        pid = upsert('projects', 'project_code', code, {
            'project_name': name, 'project_category': cat, 'priority': priority, 'description': desc,
            'location': location, 'start_date': start, 'end_date': end, 'budget': budget,
            'status': status, 'manager_id': manager_id, 'inspection_approved': 0,
            'financial_settlement_complete': 0, 'pending_issues_resolved': 0, 'client_accepted': 0
        })
        if pid:
            project_ids.append(pid)
            if engineer_id and table_exists('project_engineer_assignments') and not scalar("select id from project_engineer_assignments where project_id=? and engineer_id=?", (pid, engineer_id)):
                insert_filtered('project_engineer_assignments', {'project_id': pid, 'engineer_id': engineer_id, 'assigned_at': datetime.now().isoformat(timespec='seconds')})

    contractor_id = upsert('contractors', 'email', 'contractor@buildtrack.com', {'name': 'BuildTrack Demo Contractor', 'company_name': 'Apex Civil Works', 'phone': '9000011111', 'status': 'Active', 'project_id': project_ids[0] if project_ids else None})
    worker_id = upsert('workers', 'email', 'worker@buildtrack.com', {'name': 'Ravi Kumar', 'role': 'Worker', 'phone': '9876543210', 'category': 'Skilled Worker', 'skill_type': 'Masonry', 'contractor_id': contractor_id, 'joining_date': '2026-08-01', 'status': 'Active'})

    cat_ids = {}
    for name in ['Labor Cost','Material Cost','Equipment Cost','Transportation Cost','Maintenance Cost','Administrative Cost']:
        cid = scalar('select id from budget_categories where lower(name)=lower(?)', (name,)) if table_exists('budget_categories') else None
        if not cid:
            cid = insert_filtered('budget_categories', {'name': name, 'description': f'{name} for construction project'})
        cat_ids[name] = cid

    today = date.today()
    percentages = [0.24, 0.37, 0.15, 0.08, 0.06, 0.10]
    for idx, pid in enumerate(project_ids):
        progress = projects[idx][10]
        pbudget = projects[idx][8]
        # Budget for every demo project, so dashboard/budget pages match.
        if table_exists('budgets'):
            cur.execute('delete from budgets where project_id=?', (pid,))
            for cname, pct in zip(cat_ids.keys(), percentages):
                insert_filtered('budgets', {'project_id': pid, 'category_id': cat_ids[cname], 'allocated_amount': round(pbudget * pct, 2), 'description': 'Consistent dashboard demo budget allocation', 'status': 'Active', 'start_date': projects[idx][6], 'end_date': projects[idx][7]})
        if table_exists('cost_estimates'):
            cur.execute('delete from cost_estimates where project_id=?', (pid,))
            insert_filtered('cost_estimates', {'project_id': pid, 'category_id': cat_ids['Labor Cost'], 'item_name': 'Labour package', 'quantity': 80 + idx * 5, 'unit': 'days', 'unit_cost': 2500, 'estimated_amount': 200000 + idx * 25000, 'description': 'Consistent labour estimate', 'estimate_date': today.isoformat()})
            insert_filtered('cost_estimates', {'project_id': pid, 'category_id': cat_ids['Material Cost'], 'item_name': 'Cement and steel package', 'quantity': 1, 'unit': 'package', 'unit_cost': 450000 + idx * 30000, 'estimated_amount': 450000 + idx * 30000, 'description': 'Consistent material estimate', 'estimate_date': today.isoformat()})
        if table_exists('expenses'):
            cur.execute('delete from expenses where project_id=?', (pid,))
            spent_base = int(pbudget * (progress / 100) * 0.35)
            insert_filtered('expenses', {'project_id': pid, 'category_id': cat_ids['Material Cost'], 'expense_name': 'Material advance payment', 'amount': max(75000, spent_base * 0.55), 'description': 'Demo material payment', 'expense_date': today.isoformat(), 'payment_status': 'Paid', 'supplier': 'Dharan Building Supplies', 'reference': f'INV-DEMO-{pid:03d}', 'source_module': 'DASHBOARD_DEMO'})
            insert_filtered('expenses', {'project_id': pid, 'category_id': cat_ids['Labor Cost'], 'expense_name': 'Worker advance payment', 'amount': max(50000, spent_base * 0.30), 'description': 'Demo workforce payment', 'expense_date': today.isoformat(), 'payment_status': 'Paid', 'supplier': 'Apex Civil Works', 'reference': f'PAY-DEMO-{pid:03d}', 'source_module': 'DASHBOARD_DEMO'})
        if table_exists('project_milestones'):
            cur.execute("delete from project_milestones where project_id=? and title like 'Demo:%'", (pid,))
            m_id = insert_filtered('project_milestones', {'project_id': pid, 'title': 'Demo: Foundation Work', 'description': 'Foundation activity for dashboard progress', 'due_date': (today + timedelta(days=20)).isoformat(), 'status': 'In Progress' if progress < 55 else 'Completed'})
        else:
            m_id = None
        if table_exists('daily_progress'):
            cur.execute("delete from daily_progress where project_id=? and activity like 'Presentation demo:%'", (pid,))
            insert_filtered('daily_progress', {'project_id': pid, 'milestone_id': m_id, 'report_date': today.isoformat(), 'work_category': 'Civil Work', 'activity': 'Presentation demo: Civil Work update', 'completion_percentage': progress, 'contractor_name': 'Apex Civil Works', 'workers_present': 18 + idx, 'workers_absent': 1, 'machinery_used': 'Crane, concrete mixer, excavator', 'materials_used': 'Cement, steel, bricks', 'weather': 'Clear', 'safety_observation': 'All workers used PPE', 'quality_remarks': 'Work inspected for presentation demo', 'delay_hours': 0, 'delay_reason': '', 'comments': 'Demo progress data visible in dashboards', 'quality_verified': 1})
        if table_exists('project_schedule_activities'):
            cur.execute("delete from project_schedule_activities where project_id=? and description like '%dashboard-consistent demo%'", (pid,))
            previous = ''
            for n, activity in enumerate(['Site Preparation','Foundation Excavation','Footing Concrete','Structural Work','Finishing & Handover']):
                status = 'Completed' if n == 0 and progress >= 20 else ('In Progress' if n == 1 and progress >= 20 else 'Not Started')
                insert_filtered('project_schedule_activities', {'project_id': pid, 'activity_name': activity, 'description': 'dashboard-consistent demo schedule activity', 'start_date': (today + timedelta(days=n*7)).isoformat(), 'end_date': (today + timedelta(days=n*7+6)).isoformat(), 'dependency': previous, 'status': status, 'created_by': manager_id})
                previous = activity
        if table_exists('resources'):
            rid = upsert('resources', 'name', f'Concrete Mixer CM-{pid:02d}', {'type': 'Concrete Equipment', 'quantity': 5, 'allocated_quantity': 2, 'status': 'Allocated', 'project_id': pid})
            if rid and table_exists('resource_allocations') and not scalar('select id from resource_allocations where project_id=? and resource_id=?', (pid, rid)):
                insert_filtered('resource_allocations', {'resource_id': rid, 'project_id': pid, 'quantity': 2, 'allocation_date': today.isoformat(), 'expected_return_date': (today + timedelta(days=30)).isoformat(), 'responsible_person': 'Ravi Kumar', 'status': 'Allocated', 'worker_id': worker_id})
            if rid and table_exists('resource_utilization') and not scalar('select id from resource_utilization where project_id=? and resource_id=?', (pid, rid)):
                insert_filtered('resource_utilization', {'resource_id': rid, 'project_id': pid, 'usage_date': today.isoformat(), 'hours_used': 7 + idx, 'status': 'Used'})
        if worker_id and contractor_id and table_exists('worker_assignments') and not scalar('select id from worker_assignments where project_id=? and worker_id=?', (pid, worker_id)):
            insert_filtered('worker_assignments', {'worker_id': worker_id, 'contractor_id': contractor_id, 'project_id': pid, 'work_activity': 'Masonry and site support', 'assignment_start_date': today.isoformat(), 'assignment_end_date': (today + timedelta(days=45)).isoformat(), 'assignment_status': 'ACTIVE' if idx == 0 else 'PLANNED'})
        if worker_id and table_exists('attendance'):
            for offset, stat in [(0, 'Present'), (-1, 'Present'), (-2, 'Absent')]:
                d = (today + timedelta(days=offset)).isoformat()
                if not scalar('select id from attendance where project_id=? and worker_id=? and date=?', (pid, worker_id, d)):
                    insert_filtered('attendance', {'worker_id': worker_id, 'project_id': pid, 'date': d, 'status': stat, 'check_in_time': '08:30' if stat == 'Present' else None, 'check_out_time': '17:00' if stat == 'Present' else None, 'working_hours': 8.5 if stat == 'Present' else 0, 'remarks': 'Dashboard-consistent attendance demo', 'used': 0})

    if table_exists('reports'):
        for title, rtype in [('Project Progress Report','Project Progress'),('Resource Utilization Report','Resource Utilization'),('Budget Summary Report','Budget'),('Workforce Attendance Report','Workforce')]:
            if not scalar('select id from reports where title=?', (title,)):
                insert_filtered('reports', {'title': title, 'description': f'Demo {rtype} report for presentation', 'report_type': rtype, 'status': 'Generated'})
    if table_exists('notifications'):
        for title, msg, recipient in [
            ('Dashboard Demo Data Ready','All role dashboards now use the same project, budget, resource, procurement and workforce demo data.','ALL'),
            ('Budget Data Updated','All presentation projects have planned budget, estimates and expenses.','ADMIN'),
            ('Worker Dashboard Linked','worker@buildtrack.com is linked to Ravi Kumar and attendance records.','WORKER')
        ]:
            if not scalar('select id from notifications where title=? and message=?', (title, msg)):
                insert_filtered('notifications', {'title': title, 'message': msg, 'recipient': recipient, 'status': 'Unread', 'created_at': datetime.now().isoformat(sep=' ')})

    conn.commit()
    conn.close()

_ensure_consistent_dashboard_demo_data()


# ============================================================
# MAKE EXISTING LOCAL PROJECTS VISIBLE IN ALL ROLE DASHBOARDS
# ============================================================
def _ensure_all_local_projects_have_dashboard_data() -> None:
    """For local demo DBs, align every existing project with dashboard data.

    This prevents one role dashboard from showing projects while another role
    dashboard or module page shows empty/zero values for the same project.
    Disable with BUILDTRACK_PRESENTATION_DEMO_DATA=0.
    """
    import os, sqlite3
    from datetime import date, datetime, timedelta
    from app.database.database import DATABASE_URL
    if not DATABASE_URL.startswith('sqlite'):
        return
    if os.getenv('BUILDTRACK_PRESENTATION_DEMO_DATA', '1').strip().lower() in {'0','false','no'}:
        return
    db_file = DATABASE_URL.replace('sqlite:///', '', 1)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    def table_exists(t): return cur.execute("select 1 from sqlite_master where type='table' and name=?", (t,)).fetchone() is not None
    def cols(t): return {r['name'] for r in cur.execute(f'pragma table_info({t})')} if table_exists(t) else set()
    def scalar(sql, params=()):
        row = cur.execute(sql, params).fetchone(); return None if row is None else list(row)[0]
    def insert_filtered(t, d):
        c = cols(t); d = {k:v for k,v in d.items() if k in c}
        if not d: return None
        keys=list(d); cur.execute(f"insert into {t} ({','.join(keys)}) values ({','.join('?' for _ in keys)})", [d[k] for k in keys]); return cur.lastrowid
    def upsert(t, key, value, d):
        row=scalar(f'select id from {t} where {key}=?', (value,)) if table_exists(t) else None
        d={k:v for k,v in d.items() if k in cols(t)}
        if row:
            if d: cur.execute(f"update {t} set {','.join(k+'=?' for k in d)} where id=?", list(d.values())+[row])
            return row
        return insert_filtered(t, {key:value, **d})
    manager_id = scalar("select id from users where email='manager@buildtrack.com'") or scalar("select id from users where role='PROJECT_MANAGER' order by id limit 1")
    engineer_id = scalar("select id from users where email='engineer@buildtrack.com'") or scalar("select id from users where role='SITE_ENGINEER' order by id limit 1")
    if manager_id and table_exists('projects'):
        cur.execute('update projects set manager_id=?', (manager_id,))
    if engineer_id and table_exists('project_engineer_assignments'):
        for row in cur.execute('select id from projects').fetchall():
            if not scalar('select id from project_engineer_assignments where project_id=? and engineer_id=?', (row['id'], engineer_id)):
                insert_filtered('project_engineer_assignments', {'project_id': row['id'], 'engineer_id': engineer_id, 'assigned_at': datetime.now().isoformat(timespec='seconds')})
    contractor_id = upsert('contractors','email','contractor@buildtrack.com',{'name':'BuildTrack Demo Contractor','company_name':'Apex Civil Works','phone':'9000011111','status':'Active','project_id':1})
    worker_id = upsert('workers','email','worker@buildtrack.com',{'name':'Ravi Kumar','role':'Worker','phone':'9876543210','category':'Skilled Worker','skill_type':'Masonry','contractor_id':contractor_id,'joining_date':'2026-08-01','status':'Active'})
    cat_ids={}
    for name in ['Labor Cost','Material Cost','Equipment Cost','Transportation Cost','Maintenance Cost','Administrative Cost']:
        cid=scalar('select id from budget_categories where lower(name)=lower(?)',(name,)) if table_exists('budget_categories') else None
        if not cid: cid=insert_filtered('budget_categories',{'name':name,'description':f'{name} for construction project'})
        cat_ids[name]=cid
    vendor_id = upsert('vendors','vendor_name','Dharan Building Supplies',{'contact_person':'Dharan','contact_number':'9150164664','email':'dharan.supplies@example.com','address':'Chennai Demo Supplier Yard','category':'Raw Materials','products_services':'Cement, sand, steel and bricks','status':'ACTIVE'})
    today=date.today(); pct_alloc=[0.24,0.37,0.15,0.08,0.06,0.10]
    if not table_exists('projects'): conn.close(); return
    for idx,p in enumerate(cur.execute('select * from projects order by id').fetchall()):
        pid=p['id']; budget=float(p['budget'] or 1000000); status=p['status'] or 'Planning'; progress=60 if status in ('Completed','Closed') else 35 if status=='In Progress' else 10 if status=='Planning' else 20
        if table_exists('budgets'):
            cur.execute('delete from budgets where project_id=?',(pid,))
            for cname,pct in zip(cat_ids.keys(),pct_alloc): insert_filtered('budgets',{'project_id':pid,'category_id':cat_ids[cname],'allocated_amount':round(budget*pct,2),'description':'All-dashboard demo budget allocation','status':'Active','start_date':p['start_date'],'end_date':p['end_date']})
        if table_exists('cost_estimates') and not scalar('select id from cost_estimates where project_id=?',(pid,)):
            insert_filtered('cost_estimates',{'project_id':pid,'category_id':cat_ids['Labor Cost'],'item_name':'Labour package','quantity':80+idx,'unit':'days','unit_cost':2500,'estimated_amount':200000+idx*15000,'description':'All-dashboard labour estimate','estimate_date':today.isoformat()})
            insert_filtered('cost_estimates',{'project_id':pid,'category_id':cat_ids['Material Cost'],'item_name':'Cement and steel package','quantity':1,'unit':'package','unit_cost':420000+idx*25000,'estimated_amount':420000+idx*25000,'description':'All-dashboard material estimate','estimate_date':today.isoformat()})
        if table_exists('expenses') and not scalar('select id from expenses where project_id=?',(pid,)):
            spent=int(budget*(progress/100)*0.35)
            insert_filtered('expenses',{'project_id':pid,'category_id':cat_ids['Material Cost'],'expense_name':'Material advance payment','amount':max(60000,spent*.55),'description':'All-dashboard demo material payment','expense_date':today.isoformat(),'payment_status':'Paid','supplier':'Dharan Building Supplies','reference':f'INV-DEMO-{pid:03d}','source_module':'DASHBOARD_DEMO'})
            insert_filtered('expenses',{'project_id':pid,'category_id':cat_ids['Labor Cost'],'expense_name':'Worker advance payment','amount':max(40000,spent*.30),'description':'All-dashboard demo worker payment','expense_date':today.isoformat(),'payment_status':'Paid','supplier':'Apex Civil Works','reference':f'PAY-DEMO-{pid:03d}','source_module':'DASHBOARD_DEMO'})
        if table_exists('daily_progress') and not scalar("select id from daily_progress where project_id=? and activity like 'All-dashboard demo:%'", (pid,)):
            mid=insert_filtered('project_milestones',{'project_id':pid,'title':'All-dashboard demo milestone','description':'Milestone used for role dashboard matching','due_date':(today+timedelta(days=20)).isoformat(),'status':'In Progress' if status!='Planning' else 'Pending'})
            insert_filtered('daily_progress',{'project_id':pid,'milestone_id':mid,'report_date':today.isoformat(),'work_category':'Civil Work','activity':'All-dashboard demo: progress update','completion_percentage':progress,'contractor_name':'Apex Civil Works','workers_present':18+idx,'workers_absent':1,'machinery_used':'Concrete mixer and excavator','materials_used':'Cement and steel','weather':'Clear','safety_observation':'PPE followed','quality_remarks':'Checked for demo','delay_hours':0,'delay_reason':'','comments':'Demo progress shown consistently','quality_verified':1})
        if table_exists('project_schedule_activities') and not scalar("select id from project_schedule_activities where project_id=? and description='all-dashboard demo schedule'", (pid,)):
            previous=''
            for n,activity in enumerate(['Site Preparation','Foundation Excavation','Footing Concrete','Structural Work']):
                insert_filtered('project_schedule_activities',{'project_id':pid,'activity_name':activity,'description':'all-dashboard demo schedule','start_date':(today+timedelta(days=n*7)).isoformat(),'end_date':(today+timedelta(days=n*7+6)).isoformat(),'dependency':previous,'status':'Completed' if n==0 and progress>=20 else 'In Progress' if n==1 and progress>=20 else 'Not Started','created_by':manager_id})
                previous=activity
        rid = upsert('resources','name',f'Dashboard Concrete Mixer P{pid}',{'type':'Concrete Equipment','quantity':5,'allocated_quantity':2,'status':'Allocated','project_id':pid})
        if rid and table_exists('resource_allocations') and not scalar('select id from resource_allocations where project_id=? and resource_id=?',(pid,rid)):
            insert_filtered('resource_allocations',{'resource_id':rid,'project_id':pid,'quantity':2,'allocation_date':today.isoformat(),'expected_return_date':(today+timedelta(days=30)).isoformat(),'responsible_person':'Ravi Kumar','status':'Allocated','worker_id':worker_id})
        if rid and table_exists('resource_utilization') and not scalar('select id from resource_utilization where project_id=? and resource_id=?',(pid,rid)):
            insert_filtered('resource_utilization',{'resource_id':rid,'project_id':pid,'usage_date':today.isoformat(),'hours_used':7+idx,'status':'Used'})
        if worker_id and contractor_id and table_exists('worker_assignments') and not scalar('select id from worker_assignments where project_id=? and worker_id=?',(pid,worker_id)):
            insert_filtered('worker_assignments',{'worker_id':worker_id,'contractor_id':contractor_id,'project_id':pid,'work_activity':'Masonry and site support','assignment_start_date':today.isoformat(),'assignment_end_date':(today+timedelta(days=45)).isoformat(),'assignment_status':'ACTIVE' if idx==0 else 'PLANNED'})
        if worker_id and table_exists('attendance') and not scalar('select id from attendance where project_id=? and worker_id=? and date=?',(pid,worker_id,today.isoformat())):
            insert_filtered('attendance',{'worker_id':worker_id,'project_id':pid,'date':today.isoformat(),'status':'Present','check_in_time':'08:30','check_out_time':'17:00','working_hours':8.5,'remarks':'All-dashboard attendance demo','used':0})
    conn.commit(); conn.close()

_ensure_all_local_projects_have_dashboard_data()

# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="BuildTrack API"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SECURITY HEADERS
# ============================================================

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store")
    if str(request.url).startswith("https://"):
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(users_router)
app.include_router(auth_router)


# ============================================================
# PROJECT MANAGEMENT
# ============================================================

app.include_router(project_router)
app.include_router(project_engineer_assignment_router)
app.include_router(milestone_router)


# ============================================================
# TASK MANAGEMENT — MODULE 8
# ============================================================

app.include_router(task_router)
app.include_router(project_schedule_router)


# ============================================================
# RESOURCE MANAGEMENT
# ============================================================

app.include_router(resource_router)
app.include_router(resource_category_router)
app.include_router(resource_allocation_router)
app.include_router(resource_utilization_router)
app.include_router(machinery_router)
app.include_router(maintenance_router)


# ============================================================
# INVENTORY MANAGEMENT
# ============================================================

app.include_router(inventory_router)


# ============================================================
# WORKFORCE MANAGEMENT — MODULE 6
# ============================================================

app.include_router(workforce_category_router)
app.include_router(contractor_router)
app.include_router(worker_router)
app.include_router(worker_assignment_router)
app.include_router(attendance_router)
app.include_router(shift_router)
app.include_router(payroll_router)


# ============================================================
# OTHER MODULES
# ============================================================

app.include_router(procurement_router)
app.include_router(procurement_request_router)
app.include_router(procurement_request_item_router)
app.include_router(vendor_router)
app.include_router(purchase_order_router)
app.include_router(purchase_order_item_router)
app.include_router(invoice_router)
app.include_router(notification_router)
app.include_router(report_router)


# ============================================================
# ANALYTICS
# ============================================================

app.include_router(analytics_router)


# ============================================================
# MODULE 3 — SITE PROGRESS MONITORING
# ============================================================

app.include_router(daily_progress_router)
app.include_router(weekly_progress_router)
app.include_router(delay_record_router)
app.include_router(progress_photo_router)
app.include_router(site_activity_log_router)


# ============================================================
# MATERIAL & INVENTORY MANAGEMENT
# ============================================================

app.include_router(material_router)
app.include_router(material_request_router)
app.include_router(material_allocation_router)
app.include_router(stock_movement_router)


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

app.include_router(document_router)


# ============================================================
# MODULE 11 — BUDGET & COST MANAGEMENT
# ============================================================

app.include_router(budget_category_router)
app.include_router(budget_router)
app.include_router(cost_estimate_router)
app.include_router(expense_router)
app.include_router(budget_monitoring_router)
app.include_router(cost_comparison_router)


# ============================================================
# HOME ROUTE
# ============================================================

@app.get("/")
def home():
    return {
        "message": "BuildTrack Backend Running Successfully"
    }