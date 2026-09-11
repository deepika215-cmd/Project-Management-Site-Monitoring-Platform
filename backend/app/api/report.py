from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.report import Report
from app.models.project import Project
from app.models.daily_progress import DailyProgress
from app.models.weekly_progress import WeeklyProgress
from app.models.delay_record import DelayRecord
from app.models.project_milestone import ProjectMilestone

from app.schemas.report_schema import (
    ReportCreate,
    ReportResponse,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

import os


router = APIRouter(
    prefix="/report",
    tags=["Report"],
)

REPORT_READ_ROLES = ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "CLIENT"]
REPORT_WRITE_ROLES = ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER"]


def _ensure_report_project_id_column(db: Session):
    """Older SQLite demo databases may not have reports.project_id yet."""
    try:
        bind = db.get_bind()
        if bind.dialect.name == "sqlite":
            rows = db.execute("PRAGMA table_info(reports)").fetchall()
            names = {row[1] for row in rows}
            if "project_id" not in names:
                db.execute("ALTER TABLE reports ADD COLUMN project_id INTEGER")
                db.commit()
    except Exception:
        db.rollback()



# ============================================================
# CREATE REPORT
# ============================================================

@router.post("/", response_model=ReportResponse, dependencies=[Depends(role_required(REPORT_WRITE_ROLES))])
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
):
    _ensure_report_project_id_column(db)
    new_report = Report(
        **report.model_dump()
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report


# ============================================================
# GET ALL REPORTS
# ============================================================

@router.get("/", response_model=list[ReportResponse], dependencies=[Depends(role_required(REPORT_READ_ROLES))])
def get_reports(
    db: Session = Depends(get_db),
):
    _ensure_report_project_id_column(db)
    return db.query(Report).order_by(Report.id.desc()).all()


# ============================================================
# MODULE 10 — REPORT PREVIEW / GENERIC PDF / EXCEL EXPORT
# ============================================================

def _report_project(report, db):
    """Resolve the report project using project_id first, then legacy title/description text."""
    project_id = getattr(report, "project_id", None)
    if project_id:
        project = db.query(Project).filter(Project.id == int(project_id)).first()
        if project:
            return project

    projects = db.query(Project).all()
    text = f"{report.title or ''} {report.description or ''}".lower()
    for project in projects:
        if (project.project_name or '').lower() and (project.project_name or '').lower() in text:
            return project
    return projects[0] if len(projects) == 1 else None


def _report_preview_payload(report, db):
    project = _report_project(report, db)
    kind = (report.report_type or '').strip().lower()
    headers, rows = [], []

    if kind in {'project progress', 'progress', 'project_progress'}:
        headers = ['Record Type', 'Date / Milestone', 'Activity / Description', 'Progress / Status']
        if project:
            for item in db.query(DailyProgress).filter(DailyProgress.project_id == project.id).order_by(DailyProgress.report_date).all():
                rows.append(['Daily Progress', str(item.report_date or ''), item.activity or '', f"{item.completion_percentage or 0}%"])
            for item in db.query(ProjectMilestone).filter(ProjectMilestone.project_id == project.id).order_by(ProjectMilestone.due_date).all():
                rows.append(['Milestone', str(item.due_date or ''), item.title or '', item.status or ''])

    elif kind in {'resource utilization', 'resource', 'resources'}:
        from app.models.resource import Resource
        headers = ['Resource', 'Type', 'Total Qty', 'Allocated', 'Available', 'Utilization', 'Status']
        query = db.query(Resource)
        if project: query = query.filter((Resource.project_id == project.id) | (Resource.project_id.is_(None)))
        for item in query.order_by(Resource.id).all():
            total = float(item.quantity or 0); allocated = float(item.allocated_quantity or 0)
            util = round((allocated / total) * 100, 2) if total else 0
            rows.append([item.name or '', item.type or '', total, allocated, max(0,total-allocated), f'{util}%', item.status or ''])

    elif kind in {'workforce', 'workforce report'}:
        from app.models.worker import Worker
        from app.models.attendance import Attendance
        headers = ['Worker', 'Role', 'Category', 'Attendance Records', 'Present', 'Absent']
        for worker in db.query(Worker).order_by(Worker.id).all():
            aq = db.query(Attendance).filter(Attendance.worker_id == worker.id)
            if project: aq = aq.filter((Attendance.project_id == project.id) | (Attendance.project_id.is_(None)))
            records = aq.all(); present=sum(1 for x in records if str(x.status).lower()=='present'); absent=sum(1 for x in records if str(x.status).lower()=='absent')
            rows.append([worker.name or '', worker.role or '', worker.category or '', len(records), present, absent])

    elif kind in {'procurement', 'procurement report'}:
        from app.models.procurement_request import ProcurementRequest
        from app.models.purchase_order import PurchaseOrder
        from app.models.invoice import Invoice
        headers = ['Record Type', 'Reference', 'Item / Vendor', 'Amount / Qty', 'Status', 'Date']
        if project:
            for x in db.query(ProcurementRequest).filter(ProcurementRequest.project_id==project.id).all():
                rows.append(['Request', f'PR-{x.id}', x.item_name or '', x.quantity or 0, x.status or '', str(x.request_date or '')])
            for x in db.query(PurchaseOrder).filter(PurchaseOrder.project_id==project.id).all():
                rows.append(['Purchase Order', f'PO-{x.id}', f'Vendor #{x.vendor_id}', x.overall_amount or x.total_amount or 0, x.status or '', str(x.order_date or '')])
            for x in db.query(Invoice).filter(Invoice.project_id==project.id).all():
                rows.append(['Invoice', x.invoice_number or f'INV-{x.id}', f'Vendor #{x.vendor_id}', x.invoice_amount or 0, x.payment_status or '', str(x.invoice_date or '')])

    elif kind in {'budget', 'budget report', 'financial'}:
        from app.models.budget import Budget
        from app.models.cost_estimate import CostEstimate
        from app.models.expense import Expense
        from app.models.budget_category import BudgetCategory
        headers = ['Category', 'Planned', 'Estimated', 'Actual', 'Remaining', 'Utilization']
        if project:
            for cat in db.query(BudgetCategory).order_by(BudgetCategory.id).all():
                planned = sum(float(x.allocated_amount or 0) for x in db.query(Budget).filter(Budget.project_id==project.id,Budget.category_id==cat.id).all())
                estimated = sum(float(x.estimated_amount or 0) for x in db.query(CostEstimate).filter(CostEstimate.project_id==project.id,CostEstimate.category_id==cat.id).all())
                actual = sum(float(x.amount or 0) for x in db.query(Expense).filter(Expense.project_id==project.id,Expense.category_id==cat.id).all())
                if planned or estimated or actual:
                    util=round(actual/planned*100,2) if planned else 0
                    rows.append([cat.name, planned, estimated, actual, planned-actual, f'{util}%'])
    else:
        headers = ['Field', 'Value']
        rows = [['Title', report.title], ['Type', report.report_type or ''], ['Status', report.status or ''], ['Description', report.description or '']]

    return {
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'report_type': report.report_type,
        'status': report.status,
        'project': project.project_name if project else None,
        'project_id': project.id if project else getattr(report, 'project_id', None),
        'project_link': f'/projects/project-details/{project.id}' if project else None,
        'headers': headers,
        'rows': rows,
    }


@router.get('/{report_id}/preview', dependencies=[Depends(role_required(REPORT_READ_ROLES))])
def preview_report(report_id: int, db: Session = Depends(get_db)):
    _ensure_report_project_id_column(db)
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail='Report not found')
    return _report_preview_payload(report, db)


@router.get('/{report_id}/export', dependencies=[Depends(role_required(REPORT_READ_ROLES))])
def export_report(report_id: int, format: str = 'pdf', db: Session = Depends(get_db)):
    _ensure_report_project_id_column(db)
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report: raise HTTPException(status_code=404, detail='Report not found')
    payload = _report_preview_payload(report, db)
    fmt = format.lower()
    output_directory = 'generated_reports'; os.makedirs(output_directory, exist_ok=True)
    safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in (report.title or f'report_{report.id}'))[:80]

    if fmt == 'pdf':
        file_path = os.path.join(output_directory, f'{safe}.pdf')
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
        styles=getSampleStyleSheet(); story=[Paragraph(report.title, styles['Title']), Spacer(1,10)]
        if report.description: story += [Paragraph(report.description, styles['Normal']), Spacer(1,10)]
        data=[payload['headers']] + [[str(v if v is not None else '') for v in row] for row in payload['rows']]
        if len(data)==1: data.append(['No matching data'] + ['']*(max(1,len(payload['headers']))-1))
        table=Table(data, repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.5,colors.grey),('FONTSIZE',(0,0),(-1,-1),7),('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.append(table); doc.build(story)
        return FileResponse(file_path, filename=os.path.basename(file_path), media_type='application/pdf')

    if fmt in {'xlsx','excel'}:
        file_path=os.path.join(output_directory,f'{safe}.xlsx'); wb=Workbook(); ws=wb.active; ws.title='Report'
        ws.append([report.title]); ws.append([report.description or '']); ws.append([]); ws.append(payload['headers'])
        for cell in ws[4]: cell.font=Font(bold=True)
        for row in payload['rows']: ws.append(list(row))
        if not payload['rows']: ws.append(['No matching data'])
        for col in range(1, ws.max_column+1):
            width=max(len(str(ws.cell(r,col).value or '')) for r in range(1,ws.max_row+1)); ws.column_dimensions[get_column_letter(col)].width=min(max(width+2,12),40)
        wb.save(file_path)
        return FileResponse(file_path, filename=os.path.basename(file_path), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    raise HTTPException(status_code=400, detail='format must be pdf or xlsx')

# ============================================================
# GET REPORT BY ID
# ============================================================

@router.get("/{report_id}", response_model=ReportResponse, dependencies=[Depends(role_required(REPORT_READ_ROLES))])
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    _ensure_report_project_id_column(db)
    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return report


# ============================================================
# UPDATE REPORT
# ============================================================

@router.put("/{report_id}", response_model=ReportResponse, dependencies=[Depends(role_required(REPORT_WRITE_ROLES))])
def update_report(
    report_id: int,
    updated_report: ReportCreate,
    db: Session = Depends(get_db),
):
    _ensure_report_project_id_column(db)
    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    for key, value in updated_report.model_dump().items():
        setattr(report, key, value)

    db.commit()
    db.refresh(report)

    return report


# ============================================================
# DELETE REPORT
# ============================================================

@router.delete("/{report_id}", dependencies=[Depends(role_required(REPORT_WRITE_ROLES))])
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    db.delete(report)
    db.commit()

    return {
        "message": "Report deleted successfully"
    }


# ============================================================
# GENERATE PROJECT PDF REPORT
# ============================================================

@router.get("/project/{project_id}/pdf", dependencies=[Depends(role_required(REPORT_READ_ROLES))])
def generate_project_pdf(
    project_id: int,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Get project
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    # --------------------------------------------------------
    # Get Module 3 data
    # --------------------------------------------------------

    daily_progress = (
        db.query(DailyProgress)
        .filter(DailyProgress.project_id == project_id)
        .order_by(DailyProgress.report_date)
        .all()
    )

    weekly_progress = (
        db.query(WeeklyProgress)
        .filter(WeeklyProgress.project_id == project_id)
        .order_by(WeeklyProgress.week_start)
        .all()
    )

    delays = (
        db.query(DelayRecord)
        .filter(DelayRecord.project_id == project_id)
        .order_by(DelayRecord.delay_date)
        .all()
    )

    milestones = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.project_id == project_id)
        .order_by(ProjectMilestone.due_date)
        .all()
    )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    output_directory = "generated_reports"

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    file_name = (
        f"project_{project_id}_progress_report.pdf"
    )

    file_path = os.path.join(
        output_directory,
        file_name
    )

    # --------------------------------------------------------
    # Create PDF
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    story = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "BuildTrack - Project Progress Report",
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # --------------------------------------------------------
    # Project Information
    # --------------------------------------------------------

    project_data = [
        ["Project Name", project.project_name or ""],
        ["Project Code", project.project_code or ""],
        ["Category", project.project_category or ""],
        ["Location", project.location or ""],
        ["Start Date", str(project.start_date or "")],
        ["End Date", str(project.end_date or "")],
        ["Budget", str(project.budget or "")],
        ["Status", project.status or ""],
    ]

    project_table = Table(
        project_data,
        colWidths=[130, 350],
    )

    project_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    story.append(project_table)

    story.append(
        Spacer(1, 20)
    )

    # ========================================================
    # DAILY PROGRESS
    # ========================================================

    story.append(
        Paragraph(
            "Daily Progress Reports",
            styles["Heading2"],
        )
    )

    if daily_progress:

        daily_data = [
            [
                "Date",
                "Category",
                "Activity",
                "Completion %",
                "Contractor",
                "Workers",
                "Machinery",
                "Materials",
                "Weather",
                "Delay",
            ]
        ]

        for item in daily_progress:

            daily_data.append([
                str(item.report_date or ""),
                item.work_category or "",
                item.activity or "",
                str(item.completion_percentage or 0),
                item.contractor_name or "",
                f"P:{item.workers_present or 0} / A:{item.workers_absent or 0}",
                item.machinery_used or "",
                item.materials_used or "",
                item.weather or "",
                f"{item.delay_hours or 0} hrs",
            ])

        daily_table = Table(
            daily_data,
            repeatRows=1,
            colWidths=[
                65,
                75,
                100,
                65,
                80,
                75,
                100,
                100,
                70,
                55,
            ],
        )

        daily_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )

        story.append(daily_table)

    else:

        story.append(
            Paragraph(
                "No daily progress records found.",
                styles["Normal"],
            )
        )

    story.append(
        Spacer(1, 20)
    )

    # ========================================================
    # WEEKLY PROGRESS
    # ========================================================

    story.append(
        Paragraph(
            "Weekly Progress Reports",
            styles["Heading2"],
        )
    )

    if weekly_progress:

        weekly_data = [
            [
                "Week",
                "Work Completed",
                "Completion %",
                "Worker Hours",
                "Major Activities",
                "Delays",
                "Safety Incidents",
                "Status",
            ]
        ]

        for item in weekly_progress:

            weekly_data.append([
                f"{item.week_start or ''} to {item.week_end or ''}",
                item.work_completed or "",
                str(item.completion_percentage or 0),
                str(item.worker_hours or 0),
                item.major_activities or "",
                item.delays or "",
                item.safety_incidents or "",
                item.overall_status or "",
            ])

        weekly_table = Table(
            weekly_data,
            repeatRows=1,
            colWidths=[
                90,
                130,
                65,
                70,
                130,
                100,
                100,
                80,
            ],
        )

        weekly_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )

        story.append(weekly_table)

    else:

        story.append(
            Paragraph(
                "No weekly progress records found.",
                styles["Normal"],
            )
        )

    story.append(
        Spacer(1, 20)
    )

    # ========================================================
    # DELAYS
    # ========================================================

    story.append(
        Paragraph(
            "Delay Records",
            styles["Heading2"],
        )
    )

    if delays:

        delay_data = [
            [
                "Date",
                "Reason",
                "Duration",
                "Affected Work",
                "Impact",
            ]
        ]

        for item in delays:

            delay_data.append([
                str(item.delay_date or ""),
                item.reason or "",
                f"{item.duration_hours or 0} hrs",
                item.affected_work or "",
                item.impact or "",
            ])

        delay_table = Table(
            delay_data,
            repeatRows=1,
            colWidths=[
                80,
                150,
                70,
                150,
                220,
            ],
        )

        delay_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )

        story.append(delay_table)

    else:

        story.append(
            Paragraph(
                "No delay records found.",
                styles["Normal"],
            )
        )

    story.append(
        Spacer(1, 20)
    )

    # ========================================================
    # MILESTONES
    # ========================================================

    story.append(
        Paragraph(
            "Project Milestones",
            styles["Heading2"],
        )
    )

    if milestones:

        milestone_data = [
            [
                "Milestone",
                "Description",
                "Due Date",
                "Status",
            ]
        ]

        for item in milestones:

            milestone_data.append([
                item.title or "",
                item.description or "",
                str(item.due_date or ""),
                item.status or "",
            ])

        milestone_table = Table(
            milestone_data,
            repeatRows=1,
            colWidths=[
                180,
                300,
                100,
                100,
            ],
        )

        milestone_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )

        story.append(milestone_table)

    else:

        story.append(
            Paragraph(
                "No milestones found.",
                styles["Normal"],
            )
        )

    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------

    document.build(story)

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/pdf",
    )


# ============================================================
# GENERATE PROJECT EXCEL REPORT
# ============================================================

@router.get("/project/{project_id}/excel", dependencies=[Depends(role_required(REPORT_READ_ROLES))])
def generate_project_excel(
    project_id: int,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Get project
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    # --------------------------------------------------------
    # Get Module 3 data
    # --------------------------------------------------------

    daily_progress = (
        db.query(DailyProgress)
        .filter(DailyProgress.project_id == project_id)
        .order_by(DailyProgress.report_date)
        .all()
    )

    weekly_progress = (
        db.query(WeeklyProgress)
        .filter(WeeklyProgress.project_id == project_id)
        .order_by(WeeklyProgress.week_start)
        .all()
    )

    delays = (
        db.query(DelayRecord)
        .filter(DelayRecord.project_id == project_id)
        .order_by(DelayRecord.delay_date)
        .all()
    )

    milestones = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.project_id == project_id)
        .order_by(ProjectMilestone.due_date)
        .all()
    )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    output_directory = "generated_reports"

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    file_name = (
        f"project_{project_id}_progress_report.xlsx"
    )

    file_path = os.path.join(
        output_directory,
        file_name
    )

    # --------------------------------------------------------
    # Create workbook
    # --------------------------------------------------------

    workbook = Workbook()

    # ========================================================
    # PROJECT SUMMARY SHEET
    # ========================================================

    summary_sheet = workbook.active
    summary_sheet.title = "Project Summary"

    summary_data = [
        ["Project Name", project.project_name],
        ["Project Code", project.project_code],
        ["Category", project.project_category],
        ["Location", project.location],
        ["Start Date", project.start_date],
        ["End Date", project.end_date],
        ["Budget", project.budget],
        ["Status", project.status],
    ]

    for row in summary_data:
        summary_sheet.append(row)

    # ========================================================
    # DAILY PROGRESS SHEET
    # ========================================================

    daily_sheet = workbook.create_sheet(
        "Daily Progress"
    )

    daily_headers = [
        "Date",
        "Work Category",
        "Activity",
        "Completion %",
        "Contractor",
        "Workers Present",
        "Workers Absent",
        "Machinery Used",
        "Materials Used",
        "Weather",
        "Safety Observation",
        "Quality Remarks",
        "Quality Verified",
        "Delay Hours",
        "Delay Reason",
        "Comments",
    ]

    daily_sheet.append(daily_headers)

    for item in daily_progress:

        daily_sheet.append([
            item.report_date,
            item.work_category,
            item.activity,
            item.completion_percentage,
            item.contractor_name,
            item.workers_present,
            item.workers_absent,
            item.machinery_used,
            item.materials_used,
            item.weather,
            item.safety_observation,
            item.quality_remarks,
            item.quality_verified,
            item.delay_hours,
            item.delay_reason,
            item.comments,
        ])

    # ========================================================
    # WEEKLY PROGRESS SHEET
    # ========================================================

    weekly_sheet = workbook.create_sheet(
        "Weekly Progress"
    )

    weekly_headers = [
        "Week Start",
        "Week End",
        "Work Completed",
        "Completion %",
        "Worker Hours",
        "Major Activities",
        "Delays",
        "Safety Incidents",
        "Overall Status",
    ]

    weekly_sheet.append(weekly_headers)

    for item in weekly_progress:

        weekly_sheet.append([
            item.week_start,
            item.week_end,
            item.work_completed,
            item.completion_percentage,
            item.worker_hours,
            item.major_activities,
            item.delays,
            item.safety_incidents,
            item.overall_status,
        ])

    # ========================================================
    # DELAY SHEET
    # ========================================================

    delay_sheet = workbook.create_sheet(
        "Delay Records"
    )

    delay_headers = [
        "Delay Date",
        "Reason",
        "Duration Hours",
        "Affected Work",
        "Impact",
    ]

    delay_sheet.append(delay_headers)

    for item in delays:

        delay_sheet.append([
            item.delay_date,
            item.reason,
            item.duration_hours,
            item.affected_work,
            item.impact,
        ])

    # ========================================================
    # MILESTONES SHEET
    # ========================================================

    milestone_sheet = workbook.create_sheet(
        "Milestones"
    )

    milestone_headers = [
        "Title",
        "Description",
        "Due Date",
        "Status",
    ]

    milestone_sheet.append(milestone_headers)

    for item in milestones:

        milestone_sheet.append([
            item.title,
            item.description,
            item.due_date,
            item.status,
        ])

    # ========================================================
    # FORMAT ALL SHEETS
    # ========================================================

    for sheet in workbook.worksheets:

        # Header formatting
        for cell in sheet[1]:

            cell.font = Font(
                bold=True
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        # Cell formatting
        for row in sheet.iter_rows():

            for cell in row:

                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

        # Auto-size columns
        for column_cells in sheet.columns:

            max_length = 0

            column_letter = get_column_letter(
                column_cells[0].column
            )

            for cell in column_cells:

                try:
                    cell_length = len(
                        str(cell.value)
                    )

                    if cell_length > max_length:
                        max_length = cell_length

                except Exception:
                    pass

            sheet.column_dimensions[
                column_letter
            ].width = min(
                max_length + 2,
                40
            )

        # Freeze header row
        sheet.freeze_panes = "A2"

    # --------------------------------------------------------
    # Save workbook
    # --------------------------------------------------------

    workbook.save(file_path)

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
