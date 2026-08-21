import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { FormsModule } from "@angular/forms";
@Component({
  selector: "app-shift-scheduling",
  imports: [CommonModule, FormsModule],
  templateUrl: "./shift-scheduling.html",
  styleUrl: "./shift-scheduling.css",
})
export class ShiftScheduling {
  q = "";
  shift = "All Shifts";
  modal = "";
  rows = [
    [
      "17 Aug 2026",
      "Morning Shift",
      "06:00 AM - 02:00 PM",
      "Residential Complex",
      "32",
      "Vikram Patel",
    ],
    [
      "17 Aug 2026",
      "General Shift",
      "10:00 AM - 06:00 PM",
      "Office Building",
      "45",
      "Suresh Yadav",
    ],
    [
      "17 Aug 2026",
      "Evening Shift",
      "02:00 PM - 10:00 PM",
      "Mall Construction",
      "28",
      "Amit Singh",
    ],
    [
      "17 Aug 2026",
      "Night Shift",
      "10:00 PM - 06:00 AM",
      "Highway Project",
      "25",
      "Ramesh Kumar",
    ],
  ];
  get filtered() {
    return this.rows.filter(
      (r) =>
        (this.shift === "All Shifts" || r[1] === this.shift) &&
        r.join(" ").toLowerCase().includes(this.q.toLowerCase()),
    );
  }
  open(s: string) {
    this.modal = s;
  }
}
