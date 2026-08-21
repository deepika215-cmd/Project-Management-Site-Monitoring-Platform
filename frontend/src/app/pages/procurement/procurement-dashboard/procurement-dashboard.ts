import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-procurement-dashboard",
  imports: [CommonModule, FormsModule],
  templateUrl: "./procurement-dashboard.html",
  styleUrl: "./procurement-dashboard.css",
})
export class ProcurementDashboard {
  period = "This Week";
  modalTitle = "";
  modalMessage = "";
  readonly requests = [
    [
      "PR-2026-032",
      "Raw Materials",
      "Cement (50kg)",
      "500 Bags",
      "20 Aug 2026",
      "Pending",
    ],
    [
      "PR-2026-031",
      "Machinery",
      "Excavator Parts",
      "10 Nos",
      "18 Aug 2026",
      "Approved",
    ],
    [
      "PR-2026-030",
      "Equipment",
      "Concrete Mixer",
      "2 Nos",
      "25 Aug 2026",
      "Pending",
    ],
    [
      "PR-2026-029",
      "Safety Equipment",
      "Safety Helmets",
      "100 Nos",
      "15 Aug 2026",
      "Approved",
    ],
    [
      "PR-2026-028",
      "Office Supplies",
      "Office Chairs",
      "20 Nos",
      "12 Aug 2026",
      "Rejected",
    ],
  ];
  readonly orders = [
    [
      "PO-2026-124",
      "Shree Cement Ltd.",
      "Highway Construction",
      "Raw Materials",
      "08 Aug 2026",
      "₹ 6,75,000",
      "Delivered",
    ],
    [
      "PO-2026-123",
      "ABC Equipments",
      "Metro Project",
      "Machinery",
      "07 Aug 2026",
      "₹ 8,45,000",
      "In Transit",
    ],
    [
      "PO-2026-122",
      "Safety First Pvt. Ltd.",
      "Residential Complex",
      "Safety Equipment",
      "06 Aug 2026",
      "₹ 1,28,750",
      "Delivered",
    ],
    [
      "PO-2026-121",
      "Steel Authority India",
      "Bridge Construction",
      "Raw Materials",
      "05 Aug 2026",
      "₹ 10,35,250",
      "Approved",
    ],
    [
      "PO-2026-120",
      "Office Point",
      "Corporate Tower",
      "Office Supplies",
      "04 Aug 2026",
      "₹ 75,620",
      "Delivered",
    ],
  ];
  readonly invoices = [
    [
      "INV-2026-118",
      "ABC Equipments",
      "PO-2026-123",
      "08 Aug 2026",
      "₹ 8,45,000",
      "22 Aug 2026",
      "Pending",
    ],
    [
      "INV-2026-117",
      "Shree Cement Ltd.",
      "PO-2026-124",
      "08 Aug 2026",
      "₹ 6,75,000",
      "23 Aug 2026",
      "Pending",
    ],
    [
      "INV-2026-116",
      "Steel Authority India",
      "PO-2026-121",
      "08 Aug 2026",
      "₹ 10,35,250",
      "21 Aug 2026",
      "Overdue",
    ],
    [
      "INV-2026-115",
      "Safety First Pvt. Ltd.",
      "PO-2026-122",
      "06 Aug 2026",
      "₹ 1,28,750",
      "20 Aug 2026",
      "Pending",
    ],
    [
      "INV-2026-114",
      "Office Point",
      "PO-2026-120",
      "04 Aug 2026",
      "₹ 75,620",
      "19 Aug 2026",
      "Paid",
    ],
  ];
  readonly vendors = [
    ["Steel Authority India", "₹ 10,35,250", "15", "93%", "4.6"],
    ["Shree Cement Ltd.", "₹ 6,75,000", "12", "95%", "4.7"],
    ["ABC Equipments", "₹ 8,45,000", "10", "90%", "4.4"],
    ["Safety First Pvt. Ltd.", "₹ 3,87,820", "8", "96%", "4.8"],
    ["Office Point", "₹ 75,620", "6", "89%", "4.3"],
  ];
  open(title: string, message: string) {
    this.modalTitle = title;
    this.modalMessage = message;
  }
  close() {
    this.modalTitle = "";
    this.modalMessage = "";
  }
  changePeriod() {
    this.open(
      "Dashboard updated",
      `Showing procurement data for ${this.period.toLowerCase()}.`,
    );
  }
  exportReport() {
    const csv = [
      "PO Number,Vendor,Project,Category,Status",
      ...this.orders.map((r) => [r[0], r[1], r[2], r[3], r[6]].join(",")),
    ].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "procurement-report.csv";
    a.click();
    URL.revokeObjectURL(url);
  }
}
