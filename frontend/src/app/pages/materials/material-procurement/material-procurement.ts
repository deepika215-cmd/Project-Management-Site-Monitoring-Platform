import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-material-procurement",
  imports: [CommonModule, FormsModule],
  templateUrl: "./material-procurement.html",
  styleUrl: "./material-procurement.css",
})
export class MaterialProcurement {
  query = "";
  status = "All Status";
  modal = "";
  rows = [
    [
      "PO-2026-043",
      "Cement (OPC)",
      "Shree Cement Ltd.",
      "1,000 Bags",
      "₹4,20,000",
      "Received",
    ],
    [
      "PO-2026-042",
      "Steel (TMT 12mm)",
      "Tata Steel",
      "2,000 Kg",
      "₹1,16,000",
      "Received",
    ],
    [
      "PO-2026-041",
      "Bricks",
      "Local Supplier",
      "20,000 Nos",
      "₹1,50,000",
      "In Transit",
    ],
    [
      "PO-2026-040",
      "Sand",
      "Shree Ram Traders",
      "10 Cubic Meter",
      "₹12,000",
      "Pending",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Status" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.query.toLowerCase()),
    );
  }
  open(text: string) {
    this.modal = text;
  }
}
