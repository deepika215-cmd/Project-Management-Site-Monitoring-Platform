import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-inventory-monitoring",
  imports: [CommonModule, FormsModule],
  templateUrl: "./inventory-monitoring.html",
  styleUrl: "./inventory-monitoring.css",
})
export class InventoryMonitoring {
  query = "";
  level = "All Levels";
  modal = "";
  rows = [
    ["Cement (OPC)", "Cement", "45 Bags", "100 Bags", "Low"],
    ["Steel (TMT 12mm)", "Steel", "120 Kg", "300 Kg", "Low"],
    ["Bricks", "Masonry", "12,500 Nos", "5,000 Nos", "Available"],
    ["Electrical Wire", "Electrical", "50 Meter", "100 Meter", "Low"],
    ["PVC Pipes", "Plumbing", "30 Meter", "80 Meter", "Low"],
    ["Sand", "Aggregate", "2 Cubic Meter", "5 Cubic Meter", "Critical"],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.level === "All Levels" || r[4] === this.level) &&
        r.join(" ").toLowerCase().includes(this.query.toLowerCase()),
    );
  }
  open(text: string) {
    this.modal = text;
  }
}
