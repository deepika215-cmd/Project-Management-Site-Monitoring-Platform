import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-material-allocation",
  imports: [CommonModule, FormsModule],
  templateUrl: "./material-allocation.html",
  styleUrl: "./material-allocation.css",
})
export class MaterialAllocation {
  query = "";
  status = "All Allocations";
  modal = "";
  rows = [
    [
      "MA-2026-031",
      "Cement (OPC)",
      "Residential Complex",
      "300 Bags",
      "Amit Sharma",
      "Allocated",
    ],
    [
      "MA-2026-030",
      "Steel (TMT 12mm)",
      "Office Building",
      "1,000 Kg",
      "Rohit Verma",
      "Allocated",
    ],
    [
      "MA-2026-029",
      "Bricks",
      "Commercial Plaza",
      "8,000 Nos",
      "Neha Patel",
      "Partial",
    ],
    [
      "MA-2026-028",
      "Sand",
      "Residential Complex",
      "6 Cubic Meter",
      "Amit Sharma",
      "Pending",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Allocations" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.query.toLowerCase()),
    );
  }
  open(text: string) {
    this.modal = text;
  }
}
