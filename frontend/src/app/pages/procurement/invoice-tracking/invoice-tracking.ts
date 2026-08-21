import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-invoice-tracking",
  imports: [CommonModule, FormsModule],
  templateUrl: "./invoice-tracking.html",
  styleUrl: "./invoice-tracking.css",
})
export class InvoiceTracking {
  q = "";
  status = "All Status";
  modal = "";
  rows = [
    [
      "INV-2026-118",
      "ABC Equipments",
      "PO-2026-123",
      "₹ 8,45,000",
      "22 Aug 2026",
      "Pending",
    ],
    [
      "INV-2026-117",
      "Shree Cement Ltd.",
      "PO-2026-124",
      "₹ 6,75,000",
      "23 Aug 2026",
      "Pending",
    ],
    [
      "INV-2026-116",
      "Steel Authority India",
      "PO-2026-121",
      "₹ 10,35,250",
      "21 Aug 2026",
      "Overdue",
    ],
    [
      "INV-2026-115",
      "Safety First Pvt. Ltd.",
      "PO-2026-122",
      "₹ 1,28,750",
      "20 Aug 2026",
      "Paid",
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
