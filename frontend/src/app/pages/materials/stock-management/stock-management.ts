import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-stock-management",
  imports: [CommonModule, FormsModule],
  templateUrl: "./stock-management.html",
  styleUrl: "./stock-management.css",
})
export class StockManagement {
  query = "";
  movement = "All Movements";
  modal = "";
  rows = [
    [
      "ST-2026-112",
      "09 Aug 2026",
      "Cement (OPC)",
      "Stock In",
      "1,000 Bags",
      "PO-2026-043",
    ],
    [
      "ST-2026-111",
      "09 Aug 2026",
      "Cement (OPC)",
      "Stock Out",
      "300 Bags",
      "MA-2026-031",
    ],
    [
      "ST-2026-110",
      "08 Aug 2026",
      "Steel (TMT 12mm)",
      "Stock In",
      "2,000 Kg",
      "PO-2026-042",
    ],
    [
      "ST-2026-109",
      "08 Aug 2026",
      "Bricks",
      "Stock Out",
      "8,000 Nos",
      "MA-2026-029",
    ],
    [
      "ST-2026-108",
      "07 Aug 2026",
      "Sand",
      "Adjustment",
      "2 Cubic Meter",
      "ADJ-2026-007",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.movement === "All Movements" || r[3] === this.movement) &&
        r.join(" ").toLowerCase().includes(this.query.toLowerCase()),
    );
  }
  open(text: string) {
    this.modal = text;
  }
}
