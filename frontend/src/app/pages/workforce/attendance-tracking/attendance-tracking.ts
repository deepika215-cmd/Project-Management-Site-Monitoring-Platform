import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-attendance-tracking",
  imports: [CommonModule, FormsModule],
  templateUrl: "./attendance-tracking.html",
  styleUrl: "./attendance-tracking.css",
})
export class AttendanceTracking {
  q = "";
  status = "All Status";
  modal = "";
  rows = [
    [
      "WR-2026-001",
      "Ramesh Kumar",
      "Residential Complex",
      "08:02 AM",
      "05:31 PM",
      "Present",
    ],
    [
      "WR-2026-002",
      "Suresh Yadav",
      "Office Building",
      "08:10 AM",
      "05:40 PM",
      "Present",
    ],
    [
      "WR-2026-003",
      "Amit Singh",
      "Mall Construction",
      "08:05 AM",
      "-",
      "Absent",
    ],
    [
      "WR-2026-004",
      "Vikram Patel",
      "Highway Project",
      "08:00 AM",
      "05:20 PM",
      "Present",
    ],
    ["WR-2026-005", "Imran Khan", "Residential Complex", "-", "-", "Leave"],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Status" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
