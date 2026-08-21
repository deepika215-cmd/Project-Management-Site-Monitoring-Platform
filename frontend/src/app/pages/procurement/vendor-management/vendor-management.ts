import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-vendor-management",
  imports: [CommonModule, FormsModule],
  templateUrl: "./vendor-management.html",
  styleUrl: "./vendor-management.css",
})
export class VendorManagement {
  q = "";
  status = "All Vendors";
  modal = "";
  rows = [
    [
      "VN-001",
      "Steel Authority India",
      "Raw Materials",
      "Mumbai",
      "15",
      "4.6",
      "Active",
    ],
    [
      "VN-002",
      "Shree Cement Ltd.",
      "Raw Materials",
      "Delhi",
      "12",
      "4.7",
      "Active",
    ],
    ["VN-003", "ABC Equipments", "Machinery", "Pune", "10", "4.4", "Active"],
    [
      "VN-004",
      "Safety First Pvt. Ltd.",
      "Safety Equipment",
      "Bengaluru",
      "8",
      "4.8",
      "Pending",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Vendors" || r[6] === this.status) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
