import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-payroll-monitoring",
  imports: [CommonModule, FormsModule],
  templateUrl: "./payroll-monitoring.html",
  styleUrl: "./payroll-monitoring.css",
})
export class PayrollMonitoring {
  q = "";
  status = "All Status";
  modal = "";
  rows = [
    [
      "PR-2026-081",
      "Ramesh Kumar",
      "Residential Complex",
      "₹42,000",
      "₹42,000",
      "Paid",
    ],
    [
      "PR-2026-080",
      "Suresh Yadav",
      "Office Building",
      "₹28,000",
      "₹28,000",
      "Paid",
    ],
    [
      "PR-2026-079",
      "Amit Singh",
      "Mall Construction",
      "₹56,000",
      "₹0",
      "Pending",
    ],
    [
      "PR-2026-078",
      "Vikram Patel",
      "Highway Project",
      "₹48,000",
      "₹24,000",
      "Partial",
    ],
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
