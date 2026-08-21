import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-procurement-requests",
  imports: [CommonModule, FormsModule],
  templateUrl: "./procurement-requests.html",
  styleUrl: "./procurement-requests.css",
})
export class ProcurementRequests {
  q = "";
  status = "All Requests";
  modal = "";
  rows = [
    [
      "PR-2026-032",
      "Raw Materials",
      "Cement (50kg)",
      "Highway Construction",
      "500 Bags",
      "Pending",
    ],
    [
      "PR-2026-031",
      "Machinery",
      "Excavator Parts",
      "Metro Project",
      "10 Nos",
      "Approved",
    ],
    [
      "PR-2026-030",
      "Equipment",
      "Concrete Mixer",
      "Residential Complex",
      "2 Nos",
      "Pending",
    ],
    [
      "PR-2026-029",
      "Safety Equipment",
      "Safety Helmets",
      "Bridge Construction",
      "100 Nos",
      "Approved",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Requests" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
