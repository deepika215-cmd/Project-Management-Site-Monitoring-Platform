import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-worker-registration",
  imports: [CommonModule, FormsModule],
  templateUrl: "./worker-registration.html",
  styleUrl: "./worker-registration.css",
})
export class WorkerRegistration {
  q = "";
  type = "All Categories";
  modal = "";
  rows = [
    [
      "WR-2026-101",
      "Ramesh Kumar",
      "Skilled Worker",
      "Mason",
      "Residential Complex",
      "Active",
    ],
    [
      "WR-2026-100",
      "Suresh Yadav",
      "Unskilled Worker",
      "Helper",
      "Office Building",
      "Active",
    ],
    [
      "WR-2026-099",
      "Amit Singh",
      "Engineer",
      "Civil Engineer",
      "Mall Construction",
      "Active",
    ],
    [
      "WR-2026-098",
      "Vikram Patel",
      "Supervisor",
      "Site Supervisor",
      "Highway Project",
      "Active",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.type === "All Categories" || r[2] === this.type) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
