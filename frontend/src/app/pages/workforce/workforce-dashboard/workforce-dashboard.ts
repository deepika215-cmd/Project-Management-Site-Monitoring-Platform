import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-workforce-dashboard",
  imports: [CommonModule, FormsModule],
  templateUrl: "./workforce-dashboard.html",
  styleUrl: "./workforce-dashboard.css",
})
export class WorkforceDashboard {
  menuOpen = false;
  period = "This Week";
  modalTitle = "";
  modalMessage = "";
  readonly dates = [
    "09 Aug",
    "10 Aug",
    "11 Aug",
    "12 Aug",
    "13 Aug",
    "14 Aug",
    "15 Aug",
    "16 Aug",
  ];
  readonly categories = [
    { name: "Engineers", count: 50, pct: 20, color: "#216fe5" },
    { name: "Supervisors", count: 30, pct: 12, color: "#25a974" },
    { name: "Contractors", count: 35, pct: 14, color: "#ff9500" },
    { name: "Skilled Workers", count: 90, pct: 36, color: "#8d55cd" },
    { name: "Unskilled Workers", count: 30, pct: 12, color: "#12a9bd" },
    { name: "Consultants", count: 15, pct: 6, color: "#f05b78" },
  ];
  readonly workers = [
    [
      "WR-2026-101",
      "Ramesh Kumar",
      "Skilled Worker",
      "Mason",
      "Residential Complex",
      "15 Aug 2026",
    ],
    [
      "WR-2026-100",
      "Suresh Yadav",
      "Unskilled Worker",
      "Helper",
      "Office Building",
      "14 Aug 2026",
    ],
    [
      "WR-2026-099",
      "Amit Singh",
      "Engineer",
      "Civil Engineer",
      "Mall Construction",
      "14 Aug 2026",
    ],
    [
      "WR-2026-098",
      "Vikram Patel",
      "Supervisor",
      "Site Supervisor",
      "Highway Project",
      "13 Aug 2026",
    ],
    [
      "WR-2026-097",
      "Imran Khan",
      "Skilled Worker",
      "Carpenter",
      "Residential Complex",
      "12 Aug 2026",
    ],
  ];
  readonly attendance = [
    ["WR-2026-001", "Ramesh Kumar", "08:02 AM", "05:31 PM", "Present"],
    ["WR-2026-002", "Suresh Yadav", "08:10 AM", "05:40 PM", "Present"],
    ["WR-2026-003", "Amit Singh", "08:05 AM", "-", "Absent"],
    ["WR-2026-004", "Vikram Patel", "08:00 AM", "05:20 PM", "Present"],
    ["WR-2026-005", "Imran Khan", "08:12 AM", "05:45 PM", "Present"],
  ];
  readonly shifts = [
    [
      "17 Aug 2026",
      "Morning Shift",
      "06:00 AM - 02:00 PM",
      "Residential Complex",
      "32",
      "Vikram Patel",
    ],
    [
      "17 Aug 2026",
      "General Shift",
      "10:00 AM - 06:00 PM",
      "Office Building",
      "45",
      "Suresh Yadav",
    ],
    [
      "17 Aug 2026",
      "Evening Shift",
      "02:00 PM - 10:00 PM",
      "Mall Construction",
      "28",
      "Amit Singh",
    ],
    [
      "17 Aug 2026",
      "Night Shift",
      "10:00 PM - 06:00 AM",
      "Highway Project",
      "25",
      "Ramesh Kumar",
    ],
  ];
  toggleMenu() {
    this.menuOpen = !this.menuOpen;
  }
  open(title: string, message: string) {
    this.modalTitle = title;
    this.modalMessage = message;
  }
  close() {
    this.modalTitle = "";
    this.modalMessage = "";
  }
  periodChanged() {
    this.open(
      "Dashboard updated",
      `Showing workforce analytics for ${this.period.toLowerCase()}.`,
    );
  }
  viewWorker(row: string[]) {
    this.open(
      row[1],
      `${row[0]} is an active ${row[3]} assigned to ${row[4]}.`,
    );
  }
  exportReport() {
    const csv = [
      "Worker ID,Name,Category,Role,Project",
      ...this.workers.map((r) => r.slice(0, 5).join(",")),
    ].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "workforce-report.csv";
    a.click();
    URL.revokeObjectURL(url);
  }
}
