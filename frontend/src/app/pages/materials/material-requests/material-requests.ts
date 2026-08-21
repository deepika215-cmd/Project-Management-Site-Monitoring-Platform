import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-material-requests",
  imports: [CommonModule, FormsModule],
  templateUrl: "./material-requests.html",
  styleUrl: "./material-requests.css",
})
export class MaterialRequests {
  query = "";
  status = "All Requests";
  modal = "";
  rows = [
    [
      "MR-2026-018",
      "Cement (OPC)",
      "Residential Complex",
      "Amit Sharma",
      "200 Bags",
      "Pending",
    ],
    [
      "MR-2026-017",
      "Steel (TMT 12mm)",
      "Office Building",
      "Rohit Verma",
      "500 Kg",
      "Approved",
    ],
    [
      "MR-2026-016",
      "Bricks",
      "Commercial Plaza",
      "Neha Patel",
      "10,000 Nos",
      "Pending",
    ],
    [
      "MR-2026-015",
      "Sand",
      "Residential Complex",
      "Amit Sharma",
      "5 Cubic Meter",
      "Delivered",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Requests" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.query.toLowerCase()),
    );
  }
  open(text: string) {
    this.modal = text;
  }
}
