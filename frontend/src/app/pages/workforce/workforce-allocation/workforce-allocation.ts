import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-workforce-allocation",
  imports: [CommonModule, FormsModule],
  templateUrl: "./workforce-allocation.html",
  styleUrl: "./workforce-allocation.css",
})
export class WorkforceAllocation {
  q = "";
  status = "All Allocations";
  modal = "";
  rows = [
    [
      "WA-2026-054",
      "Residential Complex",
      "Masons",
      "32",
      "Vikram Patel",
      "Allocated",
    ],
    [
      "WA-2026-053",
      "Office Building",
      "Helpers",
      "45",
      "Suresh Yadav",
      "Allocated",
    ],
    [
      "WA-2026-052",
      "Mall Construction",
      "Engineers",
      "28",
      "Amit Singh",
      "Partial",
    ],
    [
      "WA-2026-051",
      "Highway Project",
      "Supervisors",
      "25",
      "Ramesh Kumar",
      "Pending",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Allocations" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
