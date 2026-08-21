import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-purchase-orders",
  imports: [CommonModule, FormsModule],
  templateUrl: "./purchase-orders.html",
  styleUrl: "./purchase-orders.css",
})
export class PurchaseOrders {
  q = "";
  status = "All Orders";
  modal = "";
  rows = [
    [
      "PO-2026-124",
      "Shree Cement Ltd.",
      "Highway Construction",
      "Cement (50kg)",
      "₹ 6,75,000",
      "Delivered",
    ],
    [
      "PO-2026-123",
      "ABC Equipments",
      "Metro Project",
      "Excavator Parts",
      "₹ 8,45,000",
      "In Transit",
    ],
    [
      "PO-2026-122",
      "Safety First Pvt. Ltd.",
      "Residential Complex",
      "Safety Helmets",
      "₹ 1,28,750",
      "Delivered",
    ],
    [
      "PO-2026-121",
      "Steel Authority India",
      "Bridge Construction",
      "TMT Steel",
      "₹ 10,35,250",
      "Approved",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Orders" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
