import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-supplier-management",
  imports: [CommonModule, FormsModule],
  templateUrl: "./supplier-management.html",
  styleUrl: "./supplier-management.css",
})
export class SupplierManagement {
  q = "";
  status = "All Suppliers";
  modal = "";
  rows = [
    ["SUP-001", "Shree Cement Ltd.", "Raw Materials", "Delhi", "95%", "Active"],
    ["SUP-002", "ABC Equipments", "Machinery", "Pune", "90%", "Active"],
    [
      "SUP-003",
      "Safety First Pvt. Ltd.",
      "Safety Equipment",
      "Bengaluru",
      "96%",
      "Active",
    ],
    ["SUP-004", "Office Point", "Office Supplies", "Mumbai", "89%", "Pending"],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.status === "All Suppliers" || r[5] === this.status) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
