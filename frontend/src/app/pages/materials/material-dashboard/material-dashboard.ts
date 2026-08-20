import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-material-dashboard',
  imports: [CommonModule],
  templateUrl: './material-dashboard.html',
  styleUrl: './material-dashboard.css',
})
export class MaterialDashboard {
  readonly categories = [
    { name: 'Cement', amount: 28, color: '#1769df' }, { name: 'Steel', amount: 22, color: '#16a467' },
    { name: 'Bricks', amount: 16, color: '#ffad00' }, { name: 'Sand', amount: 12, color: '#8b55cb' },
    { name: 'Concrete', amount: 10, color: '#11a5c2' }, { name: 'Electrical Materials', amount: 7, color: '#ff8129' }, { name: 'Plumbing Materials', amount: 5, color: '#f44a6c' },
  ];
  readonly requests = [
    ['MR-2026-018', 'Cement (OPC)', 'Residential Complex', 'Amit Sharma', '200 Bags', '18 Aug 2026', 'Pending'],
    ['MR-2026-017', 'Steel (TMT 12mm)', 'Office Building', 'Rohit Verma', '500 Kg', '17 Aug 2026', 'Approved'],
    ['MR-2026-016', 'Bricks', 'Commercial Plaza', 'Neha Patel', '10,000 Nos', '16 Aug 2026', 'Pending'],
    ['MR-2026-015', 'Sand', 'Residential Complex', 'Amit Sharma', '5 Cubic Meter', '15 Aug 2026', 'Delivered'],
    ['MR-2026-014', 'Electrical Wire', 'Office Building', 'Rohit Verma', '300 Meter', '14 Aug 2026', 'Approved'],
  ];
  readonly lowStock = [['Cement (OPC)', '45 Bags', '100 Bags'], ['Steel (TMT 12mm)', '120 Kg', '300 Kg'], ['Electrical Wire', '50 Meter', '100 Meter'], ['PVC Pipes', '30 Meter', '80 Meter'], ['Sand', '2 Cubic Meter', '5 Cubic Meter']];
  readonly procurement = [
    ['PO-2026-043', 'Cement (OPC)', 'Shree Cement Ltd.', '1,000 Bags', '₹420.00', '₹4,20,000.00', '08 Aug 2026', 'Received'],
    ['PO-2026-042', 'Steel (TMT 12mm)', 'Tata Steel', '2,000 Kg', '₹58.00', '₹1,16,000.00', '07 Aug 2026', 'Received'],
    ['PO-2026-041', 'Bricks', 'Local Supplier', '20,000 Nos', '₹7.50', '₹1,50,000.00', '06 Aug 2026', 'In Transit'],
    ['PO-2026-040', 'Sand', 'Shree Ram Traders', '10 Cubic Meter', '₹1,200.00', '₹12,000.00', '05 Aug 2026', 'Pending'],
  ];
}
